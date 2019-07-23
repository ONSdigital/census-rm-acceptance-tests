import functools

from behave import then, given

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import tc
from config import Config

import xml.etree.ElementTree as ET


@then('the action instruction messages are emitted to FWMT where the case has a treatment code of "{treatment_code}"')
def fwmt_messages_received(context, treatment_code):
    context.expected_sample_units = [
        sample_unit
        for sample_unit in context.sample_units.copy() if sample_unit['attributes']['TREATMENT_CODE'] == treatment_code
    ]

    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE_TEST,
                                    functools.partial(_callback, context=context))

    assert not context.expected_sample_units, 'Some messages are missing'


@given('a refusal event message is received')
def refusal_message(context):
    with RabbitContext() as rabbit:
        message = '{"event":{"type":"REFUSAL_RECEIVED","source":"eOMtThyhVNLWUZNRcBaQKxI","channel":'\
                  '"yedUsFwdkelQbxeTeQOvaScfqIOOmaa","dateTime":"2019-01-01T00:00:00.000000Z","transactionId":'\
                  '"RYtGKbgicZaHCBRQDSx"},"payload":{"refusal":{"type":"EXTRAORDINARY_REFUSAL","report":'\
                  '"VLhpfQGTMDYpsBZxvfBoeygjb","agentId":"UMaAIKKIkknjWEXJUfPxxQHeWKEJ","collectionCase":{"id":'\
                  '"dpHYZGhtgdntugzvvKAXLhM"}}}}'

        rabbit.publish_message(message, 'application/json',  Config.RABBITMQ_EVENT_EXCHANGE,
                               Config.RABBITMQ_REFUSAL_ROUTING_KEY)


@then('an action instruction cancel message is emitted to FWMT')
def refusal_received(context):
    context.seen_expected_fwmt_message = False
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE_TEST,
                                    functools.partial(_refusal_callback, context=context))
    assert context.seen_expected_fwmt_message, 'Expected message not seen'


def _callback(ch, method, _properties, body, context):
    root = ET.fromstring(body)

    if not root[0].tag == 'actionRequest':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        assert False, 'Unexpected message on Action.Field case queue'

    for index, sample_unit in enumerate(context.expected_sample_units):
        if _message_matches(sample_unit, root):
            _message_valid(sample_unit, root)
            del context.expected_sample_units[index]
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print('Have matching msg')
            break
    else:
        assert False, 'Found message on Action.Field case queue which did not match any expected sample units'

    if not context.expected_sample_units:
        ch.stop_consuming()


def _refusal_callback(ch, method, _properties, body, context):
    root = ET.fromstring(body)

    if not root[0].tag == 'actionCancel':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        assert False, 'Unexpected message on Action.Field queue'

    tc.assertEqual('dpHYZGhtgdntugzvvKAXLhM', root.find('.//caseId').text)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    context.seen_expected_fwmt_message = True
    ch.stop_consuming()


def _message_matches(sample_unit, root):
    return root.find('.//arid').text == sample_unit['attributes']['ARID']


def _message_valid(sample_unit, root):
    tc.assertEqual(sample_unit['attributes']['LATITUDE'], root.find('.//latitude').text)
    tc.assertEqual(sample_unit['attributes']['LONGITUDE'], root.find('.//longitude').text)
    tc.assertEqual(sample_unit['attributes']['POSTCODE'], root.find('.//postcode').text)
