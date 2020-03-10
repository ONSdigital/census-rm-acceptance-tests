import functools
import json

import requests
from behave import step
from str2bool import str2bool

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

case_api_url = f'{Config.CASEAPI_SERVICE}/cases/'


@step('the action instruction is emitted to FWMT where case has a secureEstablishment value of "{expected_value}"')
def fwmt_message_received_with_ce1_complete(context, expected_value):
    if expected_value == "none":
        converted_expected_value = None
    else:
        converted_expected_value = str2bool(expected_value)

    _check_emitted_action_instructions(context, converted_expected_value)


@step('the case can be retrieved from the case API service and has a secureEstablishment value of "{expected_value}"')
def get_case_by_id(context, expected_value):
    case_id = context.case_created_events[0]['payload']['collectionCase']['id']
    response = requests.get(f'{case_api_url}{case_id}')
    test_helper.assertEqual(response.status_code, 200, 'Case not found')
    case_details = response.json()

    assert case_details['ceSecure'] == str2bool(expected_value), "Unexpected secureEstablishment value"


def _check_emitted_action_instructions(context, expected_value):
    context.expected_cases_for_action = context.case_created_events

    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE,
                                    functools.partial(fieldwork_message_callback, context=context,
                                                      expected_value=expected_value))

    test_helper.assertFalse(context.expected_cases_for_action,
                            msg="Didn't find all expected fieldwork action instruction messages")


def fieldwork_message_callback(ch, method, _properties, body, context, expected_value):
    action_instruction = json.loads(body)

    if not action_instruction['actionInstruction'] == 'CREATE':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        test_helper.fail(f'Unexpected message on {Config.RABBITMQ_OUTBOUND_FIELD_QUEUE} case queue. '
                         f'Got "{action_instruction["actionInstruction"]}", wanted "CREATE"')

    for index, _ in enumerate(context.expected_cases_for_action):
        _check_expected_secure_establishment_value(action_instruction, expected_value)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        del context.expected_cases_for_action[index]
        break

    else:
        test_helper.fail(
            f'Found message on {Config.RABBITMQ_OUTBOUND_FIELD_QUEUE} case queue which did not '
            f'match any expected sample units')

    if not context.expected_cases_for_action:
        ch.stop_consuming()


def _check_expected_secure_establishment_value(action_instruction, expected_value):
    if expected_value is None:
        try:
            action_instruction['secureEstablishment']
            assert False, "secureEstablishment value present in message when it shouldn't be there"
        except KeyError:
            pass

    else:
        if not action_instruction['secureEstablishment'] == expected_value:
            assert False, "secureEstablishment was unexpected value"
        else:
            pass
