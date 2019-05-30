import functools

from behave import then

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from config import Config

import xml.etree.ElementTree as ET


@then('the action instruction messages are emitted to FWMT')
def fwmt_messages_received(context):
    context.expected_sample_units = context.sample_units.copy()
    context.case_created_events = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE,
                                    functools.partial(_callback, context=context))

    assert not context.expected_sample_units, 'Some messages are missing'


def _callback(ch, method, _properties, body, context):

    root = ET.fromstring(body)

    if not root[0].tag == 'actionRequest':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        assert False, 'Unexpected message on Action.Field case queue'
        return

    for index, sample_unit in enumerate(context.expected_sample_units):
        if _message_matches(sample_unit, root):
            del context.expected_sample_units[index]
            ch.basic_ack(delivery_tag=method.delivery_tag)
            break
    else:
        assert False, 'Could not find sample unit'

    if not context.expected_sample_units:
        ch.stop_consuming()


def _message_matches(sample_unit, root):
    return root.find('.//arid').text == sample_unit['attributes']['ARID']
