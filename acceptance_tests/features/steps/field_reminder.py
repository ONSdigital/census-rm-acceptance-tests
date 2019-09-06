import functools
import xml.etree.ElementTree as ET

from behave import then, step

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step('the action instruction messages for only the HH case are emitted to FWMT where the case has a treatment code of'
      ' "{treatment_code}"')
@step('the action instruction messages are emitted to FWMT where the case has a treatment code of "{treatment_code}"')
def fwmt_messages_received(context, treatment_code):
    context.expected_cases_for_action = [
        case_created['payload']['collectionCase'] for case_created in context.case_created_events
        if case_created['payload']['collectionCase']['treatmentCode'] == treatment_code
    ]

    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE_TEST,
                                    functools.partial(fieldwork_message_callback, context=context))

    test_helper.assertFalse(context.expected_cases_for_action,
                            msg="Didn't find all expected fieldwork action instruction messages")


def fieldwork_message_callback(ch, method, _properties, body, context):
    action_instruction = ET.fromstring(body)

    if not action_instruction[0].tag == 'actionRequest':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        test_helper.fail('Unexpected message on Action.Field case queue')

    for index, case in enumerate(context.expected_cases_for_action):
        if _message_matches(case, action_instruction):
            _message_valid(case, action_instruction)
            del context.expected_cases_for_action[index]
            ch.basic_ack(delivery_tag=method.delivery_tag)
            break
    else:
        test_helper.fail(msg='Found message on Action.Field case queue which did not match any expected sample units')

    if not context.expected_cases_for_action:
        ch.stop_consuming()


def _message_matches(case, action_instruction):
    return action_instruction.find('.//caseId').text == case['id']


def _message_valid(case, action_instruction):
    test_helper.assertEqual(case['address']['latitude'], action_instruction.find('.//latitude').text)
    test_helper.assertEqual(case['address']['longitude'], action_instruction.find('.//longitude').text)
    test_helper.assertEqual(case['address']['postcode'], action_instruction.find('.//postcode').text)
    test_helper.assertEqual('false', action_instruction.find('.//undeliveredAsAddress').text)
    test_helper.assertEqual('false', action_instruction.find('.//blankQreReturned').text)
    test_helper.assertEqual('CENSUS', action_instruction.find('.//surveyName').text)
    test_helper.assertEqual(case['address']['estabType'], action_instruction.find('.//estabType').text)
    test_helper.assertEqual(case['address']['arid'], action_instruction.find('.//arid').text)
