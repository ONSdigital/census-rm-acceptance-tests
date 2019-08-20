import functools
import json
import time

import requests
from behave import step

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context
from config import Config

notify_stub_url = f'{Config.NOTIFY_STUB_SERVICE}'
get_cases_url = f'{Config.CASEAPI_SERVICE}/cases/'


def get_first_case(context):
    return context.case_created_events[0]['payload']['collectionCase']


@step('a PQ fulfilment request event with fulfilment code "{pack_code}" is received by RM')
def send_fulfilment_requested_event(context, pack_code):
    context.first_case = get_first_case(context)

    message = json.dumps(
        {
            "event": {
                "type": "FULFILMENT_REQUESTED",
                "source": "CONTACT_CENTRE_API",
                "channel": "CC",
                "dateTime": "2019-07-07T22:37:11.988+0000",
                "transactionId": "d2541acb-230a-4ade-8123-eee2310c9143"
            },
            "payload": {
                "fulfilmentRequest": {
                    "fulfilmentCode": pack_code,
                    "caseId": context.first_case['id'],
                    "contact": {
                        "title": "Mrs",
                        "forename": "Test",
                        "surname": "McTest"
                    }
                }
            }
        }
    )

    time.sleep(2)
    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_FULFILMENT_REQUESTED_ROUTING_KEY)


@when('a UAC fulfilment request "{fulfilment_code}" message for a created case is sent')
def create_uac_fulfilment_message(context, fulfilment_code):
    requests.get(f'{notify_stub_url}/reset')
    context.fulfilment_requested_case_id = context.uac_created_events[0]['payload']['uac']['caseId']

    message = json.dumps(
        {
            "event": {
                "type": "FULFILMENT_REQUESTED",
                "source": "CONTACT_CENTRE_API",
                "channel": "CC",
                "dateTime": "2019-07-07T22:37:11.988+0000",
                "transactionId": "d2541acb-230a-4ade-8123-eee2310c9143"
            },
            "payload": {
                "fulfilmentRequest": {
                    "fulfilmentCode": fulfilment_code,
                    "caseId": context.fulfilment_requested_case_id,
                    "contact": {
                        "telNo": "01234567",
                        "address": "abc road"
                    }
                }
            }
        }
    )

    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_FULFILMENT_REQUESTED_ROUTING_KEY)


@step("a fulfilment request event is logged")
def check_case_events_logged(context):
    time.sleep(2)  # Give case processor a chance to process the fulfilment request event
    response = requests.get(f'{get_cases_url}{context.fulfilment_requested_case_id}', params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        if case_event['description'] == 'Fulfilment Request Received':
            return
    assert False


@step("notify api was called")
def check_notify_api_call(context):
    response = requests.get(f'{notify_stub_url}/log')
    assert response.status_code == 200, "Unexpected status code"
    response_json = response.json()
    assert len(response_json) == 1, "Incorrect number of responses"
    assert response_json[0]["phone_number"] == '01234567', "Invalid expected phone number"


@step("the fulfilment request event is logged")
def check_case_events(context):
    time.sleep(2)  # Give case processor a chance to process the fulfilment request event
    response = requests.get(f'{get_cases_url}{context.first_case["id"]}', params={'caseEvents': True})
    assert 200 <= response.status_code <= 299, 'Get cases API call failed'
    cases = response.json()
    assert any(case_event['description'] == 'Fulfilment Request Received' for case_event in cases['caseEvents'])


@step("a new child case is emitted to RH and Action Scheduler")
def child_case_is_emitted(context):
    context.messages_received = []

    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=1,
                                                      type_filter='CASE_CREATED'))
    assert len(context.messages_received) == 1
    add = context.messages_received[0]['payload']['collectionCase']['address']
    child_case_arid = context.messages_received[0]['payload']['collectionCase']['address']['estabArid']
    parent_case_arid = _get_parent_case_arid(context)

    assert child_case_arid == parent_case_arid, "Parent and child Arids must match to link cases"


def _get_parent_case_arid(context):
    response = requests.get(f'{get_cases_url}{context.fulfilment_requested_case_id}')
    return response.json()['estabArid']
