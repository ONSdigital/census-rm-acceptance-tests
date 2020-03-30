import json

import requests
from behave import step

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
            routing_key=Config.RABBITMQ_INVALID_ADDRESS_ROUTING_KEY)


@step("an AddressTypeChanged event is sent")
def address_type_changed_event_is_sent(context):
    message = json.dumps(
        {
            "event": {
                "type": "ADDRESS_TYPE_CHANGED",
                "source": "FIELDWORK_GATEWAY",
                "channel": "FIELD",
                "dateTime": "2011-08-12T20:17:46.384Z",
                "transactionId": "c45de4dc-3c3b-11e9-b210-d663bd873d93"
            },
            "payload": {
                "addressTypeChange": {
                    "collectionCase": {
                        "id": str(context.case_created_events[0]['payload']['collectionCase']['id']),
                        "ceExpectedResponses": "20",
                        "address": {
                            "orgName": "bobs",
                            "uprn": "XXXXXXXXXXXXX",
                            "arid": "XXXXX",
                            "addressType": "CE",
                            "estabType": "XXX"
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
            routing_key=Config.RABBITMQ_INVALID_ADDRESS_ROUTING_KEY)


@step("an Address Modified Event is sent")
def send_address_modified_event(context):
    message = json.dumps(
        {
            "event": {
                "type": "ADDRESS_MODIFIED",
                "source": "CONTACT_CENTRE_API",
                "channel": "CC",
                "dateTime": "2011-08-12T20:17:46.384Z",
                "transactionId": "c45de4dc-3c3b-11e9-b210-d663bd873d93"
            },
            "payload": {
                "addressModification": {
                    "collectionCase": {
                        "id": str(context.case_created_events[0]['payload']['collectionCase']['id']),
                    },
                    "originalAddress": {
                        "addressLine1": "1 main street",
                        "addressLine2": "upper upperingham",
                        "addressLine3": "",
                        "townName": "upton",
                        "postcode": "UP103UP",
                        "region": "E"
                    },
                    "newAddress": {
                        "addressLine1": "1a main street",
                        "addressLine2": "upper upperingham",
                        "addressLine3": "",
                        "townName": "upton",
                        "postcode": "UP103UP",
                        "region": "E"
                    }
                }
            }
        }

    )
    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_INVALID_ADDRESS_ROUTING_KEY)
