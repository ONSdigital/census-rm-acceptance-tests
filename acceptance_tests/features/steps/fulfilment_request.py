import json
import time

import requests
from behave import step

from acceptance_tests.features.steps.case_events import get_first_case_created_event
from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import purge_queues
from config import Config

case_api_url = f'{Config.CASEAPI_SERVICE}/cases/'


def get_first_case(context):
    return context.case_created_events[0]['payload']['collectionCase']


@step('a PQ fulfilment request event with fulfilment code "{pack_code}" is received by RM')
def send_fulfilment_requested_event(context, pack_code):
    context.fulfilment_requested_case = get_first_case(context)

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
                    "caseId": context.fulfilment_requested_case['id'],
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


@step("the fulfilment request event is logged")
def check_case_events(context):
    time.sleep(2)  # Give case processor a chance to process the fulfilment request event
    response = requests.get(f'{case_api_url}{context.fulfilment_requested_case["id"]}', params={'caseEvents': True})
    response_json = response.json()
    assert any(case_event['description'] == 'Fulfilment Request Received' for case_event in response_json['caseEvents'])
