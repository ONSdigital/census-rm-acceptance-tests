import functools
import json

import requests
from behave import step
from retrying import retry

from acceptance_tests.features.steps.event_log import check_if_event_list_is_exact_match
from acceptance_tests.features.steps.receipt import _field_work_cancel_callback
from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

caseapi_url = f'{Config.CASEAPI_SERVICE}/cases/'


def _send_refusal_msg_to_rabbit(case_id):
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
                    "type": "HARD_REFUSAL",
                    "report": "Test refusal",
                    "agentId": None,
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


@step("a refusal message for the created case is received")
def create_refusal(context):
    context.refused_case_id = context.case_created_events[0]['payload']['collectionCase']['id']

    _send_refusal_msg_to_rabbit(context.refused_case_id)


@step("a refusal message for the created CCS case is received")
def create_ccs_refusal(context):
    context.refused_case_id = context.case_id

    _send_refusal_msg_to_rabbit(context.refused_case_id)


@step("the case is marked as refused")
@retry(stop_max_attempt_number=10, wait_fixed=1000)
def check_case_events(context):
    response = requests.get(f'{caseapi_url}{context.refused_case_id}', params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        if case_event['description'] == 'Refusal Received':
            return
    test_helper.fail('Did not find "Refusal Received" event')


@step('a CANCEL action instruction is emitted to FWMT')
def refusal_received(context):
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE,
                                    functools.partial(_field_work_cancel_callback, context=context))

    test_helper.assertEqual(context.fwmt_emitted_case_id, context.refused_case_id)
    test_helper.assertEqual(context.addressType, 'HH')


@step("the events logged for the refusal case are {expected_event_list}")
def check_refusal_event_logging(context, expected_event_list):
    check_if_event_list_is_exact_match(expected_event_list, context.refused_case_id)
