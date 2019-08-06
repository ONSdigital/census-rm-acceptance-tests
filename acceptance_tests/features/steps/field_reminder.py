import functools
import xml.etree.ElementTree as ET

from behave import then

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import tc
from config import Config


@then('the action instruction messages are emitted to FWMT where the case has a treatment code of "{treatment_code}"')
def fwmt_messages_received(context, treatment_code):
    context.expected_sample_units = [
        sample_unit
        for sample_unit in context.sample_units.copy() if sample_unit['attributes']['TREATMENT_CODE'] == treatment_code
    ]

    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE_TEST,
                                    functools.partial(_callback, context=context))

    assert not context.expected_sample_units, 'Some messages are missing'


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


def _message_matches(sample_unit, root):
    return root.find('.//arid').text == sample_unit['attributes']['ARID']


def _message_valid(sample_unit, root):
    tc.assertEqual(sample_unit['attributes']['LATITUDE'], root.find('.//latitude').text)
    tc.assertEqual(sample_unit['attributes']['LONGITUDE'], root.find('.//longitude').text)
    tc.assertEqual(sample_unit['attributes']['POSTCODE'], root.find('.//postcode').text)
    tc.assertEqual('false', root.find('.//undeliveredAsAddress').text)
    tc.assertEqual('false', root.find('.//blankQreReturned').text)
    tc.assertEqual('CENSUS', root.find('.//surveyName').text)
    tc.assertEqual(sample_unit['attributes']['ESTAB_TYPE'], root.find('.//estabType').text)
