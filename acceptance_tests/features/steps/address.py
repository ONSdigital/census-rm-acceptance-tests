import json
import uuid
from time import sleep

import requests
from behave import step

from acceptance_tests.utilities.event_helper import check_case_created_message_is_emitted
from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

caseapi_url = f'{Config.CASEAPI_SERVICE}/cases/'


@step('an invalid address message is sent from "{sender}"')
def invalid_address_message(context, sender):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']

    _send_invalid_address_message_to_rabbit(context.first_case['id'], sender)


@step('an invalid address message for the CCS case is sent from "{sender}"')
def invalid_ccs_address_message(context, sender):
    context.first_case = context.ccs_case

    # TODO: Other tests match on this key structure. Remove when we've settled on case API fields
    context.first_case['survey'] = context.ccs_case['surveyType']

    _send_invalid_address_message_to_rabbit(context.first_case['id'], sender)


@step("the case event log records invalid address")
def check_case_events(context):
    response = requests.get(f"{caseapi_url}{context.first_case['id']}", params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        if case_event['description'] == 'Invalid address':
            return
    test_helper.fail('Did not find expected invalid address event')


@step('a NEW_ADDRESS_REPORTED event is sent from "{sender}"')
def new_address_reported_event(context, sender):
    context.case_id = str(uuid.uuid4())
    context.collection_exercise_id = str(uuid.uuid4())
    message = json.dumps(
        {
            "event": {
                "type": "NEW_ADDRESS_REPORTED",
                "source": "FIELDWORK_GATEWAY",
                "channel": sender,
                "dateTime": "2011-08-12T20:17:46.384Z",
                "transactionId": "d9126d67-2830-4aac-8e52-47fb8f84d3b9"
            },
            "payload": {
                "newAddress": {
                    "sourceCaseId": "16f587e9-9475-4653-a13e-501d1d2c694e",
                    "collectionCase": {
                        "id": context.case_id,
                        "caseType": "SPG",
                        "survey": "CENSUS",
                        "fieldcoordinatorId": "SO_23",
                        "fieldofficerId": "SO_23_123",
                        "collectionExerciseId": context.collection_exercise_id,
                        "address": {
                            "addressLine1": "123",
                            "addressLine2": "Fake caravan park",
                            "addressLine3": "The long road",
                            "townName": "Trumpton",
                            "postcode": "SO190PG",
                            "region": "E",
                            "addressType": "SPG",
                            "addressLevel": "U",
                            "latitude": "50.917428",
                            "longitude": "-1.238193"
                        }
                    }
                }
            }
        }
    )
    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_ADDRESS_ROUTING_KEY)


@step('the case can be retrieved')
def retrieve_case(context):
    response = requests.get(f'{caseapi_url}{context.case_id}?caseEvents=true')
    test_helper.assertEqual(response.status_code, 200, 'Case not found')
    context.first_case = response.json()


@step('a case created event is emitted')
def check_case_created_event(context):
    check_case_created_message_is_emitted(context)


def _send_invalid_address_message_to_rabbit(case_id, sender):
    message = json.dumps(
        {
            "event": {
                "type": "ADDRESS_NOT_VALID",
                "source": "FIELDWORK_GATEWAY",
                "channel": sender,
                "dateTime": "2019-07-07T22:37:11.988+0000",
                "transactionId": "d2541acb-230a-4ade-8123-eee2310c9143"
            },
            "payload": {
                "invalidAddress": {
                    "reason": "DEMOLISHED",
                    "collectionCase": {
                        "id": case_id
                    }
                }
            }
        }
    )
    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_ADDRESS_ROUTING_KEY)
