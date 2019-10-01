import json
import uuid

import requests
from behave import step

from acceptance_tests.utilities.rabbit_context import RabbitContext
from config import Config

caseapi_url = f'{Config.CASEAPI_SERVICE}/cases/'


@step("a CCS Property Listed event is sent")
def send_ccs_property_listed_event(context):
    context.fieldwork_case = uuid.uuid4()

    message = json.dumps({
        "event": {
            "type": "CCS_ADDRESS_LISTED",
            "source": "FIELDWORK_GATEWAY",
            "channel": "FIELD",
            "dateTime": "2011-08-12T20:17:46.384Z",
            "transactionId": "c45de4dc-3c3b-11e9-b210-d663bd873d93"
        },
        "payload": {
            "CCSProperty": {
                "collectionCase": {
                    "id": context.fieldwork_case
                },
                "sampleUnit": {
                    "addressType": "HH",
                    "estabType": "",
                    "addressLevel": "U",
                    "organisationName": "",
                    "addressLine1": "1 main street",
                    "addressLine2": "upper upperingham",
                    "addressLine3": "",
                    "townName": "upton",
                    "postcode": "UP103UP",
                    "latitude": "50.863849",
                    "longitude": "-1.229710",
                    "fieldcoordinatorId": "XXXXXXXXXX",
                    "fieldofficerId": "XXXXXXXXXXXXX"
                },
                "uac": {
                    "questionnaireId": "1110000009"
                },
                "refusal": {
                    "type": "HARD_REFUSAL",
                    "report": "respondent too busy",
                    "agentId": "110001"
                },
                "invalidAddress": {
                    "reason": "DEMOLISHED"
                }
            }
        }
    })

    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_CCS_PROPERTY_LISTING_ROUTING_KEY)


@step("the CCS Property Listed case is created")
def check_case_created(context):
    response = requests.get(f"{caseapi_url}{context.context.fieldwork_case}", params={'caseEvents': True})
    assert response.status_code == 200, 'CCS Property Listed case has not been created'
