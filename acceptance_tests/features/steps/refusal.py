import functools
import json

import requests
from behave import step
from retrying import retry

from acceptance_tests.utilities.event_helper import check_if_event_list_is_exact_match
from acceptance_tests.utilities.fieldwork_helper import fieldwork_message_callback, field_work_cancel_callback
from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


def _send_refusal_msg_to_rabbit(case_id, refusal_type):
    message = json.dumps(
        {
            "event": {
                "type": "REFUSAL_RECEIVED",
                "source": "CONTACT_CENTRE_API",
                "channel": "CC",
                "dateTime": "2019-07-07T22:37:11.988+0000",
                "transactionId": "d2541acb-230a-4ade-8123-eee2310c9143"
            },
            "payload": {
                "refusal": {
                    "type": refusal_type,
                    "report": "Test refusal",
                    "agentId": None,
                    "callId": "8f04b136-d13c-4d88-9068-331560a26bec",
                    "collectionCase": {
                        "id": case_id
                    },
                    "contact": {
                        "title": "Mr",
                        "forename": "Test",
                        "surname": "Testing",
                        "telNo": "01234123123"
                    },
                    "address": {
                        "addressLine1": "123",
                        "addressLine2": "Fake Street",
                        "addressLine3": "",
                        "townName": "Test Town",
                        "postcode": "XX1 XX1",
                        "region": "W",
                        "uprn": "123456789143"
                    }
                }
            }
        }
    )

    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_REFUSAL_ROUTING_KEY)


@step('a refusal message for the created case is received of type "{refusal_type}"')
def create_refusal(context, refusal_type):
    context.refused_case_id = context.case_created_events[0]['payload']['collectionCase']['id']
    _send_refusal_msg_to_rabbit(context.refused_case_id, refusal_type)


@step("a refusal message for the created CCS case is received")
def create_ccs_refusal(context):
    context.refused_case_id = context.case_id
    _send_refusal_msg_to_rabbit(context.refused_case_id, 'HARD_REFUSAL')


@step("the case is marked as refused")
@retry(stop_max_attempt_number=10, wait_fixed=1000)
def check_case_events(context):
    response = requests.get(f'{Config.CASE_API_CASE_URL}{context.refused_case_id}', params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        if case_event['description'] == 'Refusal Received':
            return
    test_helper.fail('Did not find "Refusal Received" event')


@step('a CANCEL action instruction is emitted to FWMT')
def refusal_received(context):
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE,
                                    functools.partial(field_work_cancel_callback, context=context))

    test_helper.assertEqual(context.fwmt_emitted_case_id, context.refused_case_id)
    test_helper.assertEqual(context.addressType, 'HH')


@step("the events logged for the refusal case are {expected_event_list}")
def check_refusal_event_logging(context, expected_event_list):
    check_if_event_list_is_exact_match(expected_event_list, context.refused_case_id)


@step("Only unrefused cases are sent to field")
def only_unrefused_cases_are_sent_to_field(context):
    context.expected_cases_for_action = [
        case_created['payload']['collectionCase'] for case_created in context.case_created_events
        if case_created['payload']['collectionCase']['id'] != context.refused_case_id
    ]
    context.fieldwork_case_ids = [case['id'] for case in context.expected_cases_for_action]

    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE,
                                    functools.partial(fieldwork_message_callback, context=context))

    test_helper.assertFalse(context.expected_cases_for_action,
                            msg="Didn't find all expected fieldwork action instruction messages")
