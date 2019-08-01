import json

import requests
from behave import step

from acceptance_tests.utilities.rabbit_context import RabbitContext
from config import Config

caseapi_url = f'{Config.CASEAPI_SERVICE}/cases/'


@step("a refusal message for a created case is received")
def create_refusal(context):
    context.refused_case_id = context.uac_created_events[0]['payload']['uac']['caseId']
    context.refused_questionnaire_id = context.uac_created_events[0]['payload']['uac']['questionnaireId']

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
                    "questionnaireId": context.refused_questionnaire_id,
                    "type": "HARD_REFUSAL",
                    "report": "Test refusal",
                    "agentId": None,
                    "collectionCase": {
                        "id": context.refused_case_id
                    },
                    "contact": {
                        "title": "Mr",
                        "forename": "Test",
                        "surname": "Testing",
                        "email": None,
                        "telNo": "01234123123"
                    },
                    "address": {
                        "addressLine1": "123",
                        "addressLine2": "Fake Street",
                        "addressLine3": "",
                        "townName": "Test Town",
                        "postcode": "XX1 XX1",
                        "region": "W"
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


@step("the case is marked as refused")
def check_case_events(context):
    response = requests.get(f'{caseapi_url}{context.refused_case_id}', params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        if case_event['description'] == 'Refusal Received':
            return
    assert False
