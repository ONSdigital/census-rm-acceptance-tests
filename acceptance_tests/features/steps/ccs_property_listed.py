import functools
import json
import uuid

import requests
from behave import step, then
from retrying import retry

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context
from config import Config

caseapi_url = f'{Config.CASEAPI_SERVICE}/cases/'


@step("a CCS Property Listed event is sent")
def send_ccs_property_listed_event(context):
    context.case_id = str(uuid.uuid4())

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
                    "id": context.case_id
                },
                "sampleUnit": {
                    "addressType": "NR",
                    "estabType": "Non-residential",
                    "addressLevel": "U",
                    "organisationName": "Testy McTest",
                    "addressLine1": "123 Fake street",
                    "addressLine2": "Upper upperingham",
                    "addressLine3": "Newport",
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
@retry(stop_max_attempt_number=10, wait_fixed=1000)
def check_case_created(context):
    response = requests.get(f"{caseapi_url}{context.case_id}")
    assert response.status_code == 200, 'CCS Property Listed case not found'

    response_json = response.json()
    assert response_json['caseType'] == 'NR'    # caseType is derived from addressType for CCS


@then("the correct ActionInstruction is sent to FWMT")
def check_correct_CCS_actionInstruction_sent_to_FWMT(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE_TEST,
                                    functools.partial(
                                        store_all_msgs_in_context, context=context,
                                        expected_msg_count=1,
                                        type_filter='CASE_UPDATED'))

    assert len(context.messages_received) == 1
    emitted_action_instruction = context.messages_received[0]
    assert emitted_action_instruction == 1

