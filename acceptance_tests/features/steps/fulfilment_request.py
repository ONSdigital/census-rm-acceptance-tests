import json
import requests
from behave import step

from acceptance_tests.utilities.rabbit_context import RabbitContext
from config import Config

caseapi_url = f'{Config.CASEAPI_SERVICE}/cases/'


@step("a fulfilment request message for a created case is sent")
def create_refusal(context):
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
                    "fulfilmentCode": "P_IC_ICL1",
                    "caseId": context.fulfilment_requested_case_id,
                    "address": "",
                    "contact": ""
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
def check_case_events(context):
    response = requests.get(f'{caseapi_url}{context.fulfilment_requested_case_id}', params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        if case_event['description'] == 'Fulfilment Request Received':
            return
    assert False
