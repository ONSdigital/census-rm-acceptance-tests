import json
import time

import requests
from behave import step

from acceptance_tests.utilities.rabbit_context import RabbitContext
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


@step("a UAC fulfilment request message for a created case is sent")
def create_uac_fulfilment_message(context):
    requests.get(f'{notify_stub_url}/reset')
    context.case_for_events_check = {'id': context.uac_created_events[0]['payload']['uac']['caseId']}

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
                    "fulfilmentCode": "UACHHT1",
                    "caseId": context.case_for_events_check['id'],
                    "contact": {
                        "telNo": "01234567"
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
