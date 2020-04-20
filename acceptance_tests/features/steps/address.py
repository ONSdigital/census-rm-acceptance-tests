import json
import uuid

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


@step('a NEW_ADDRESS_REPORTED event is sent from "{sender}" without sourceCaseId')
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
                    "sourceCaseId": None,
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
                            "region": "E00001234",
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


@step('a NEW_ADDRESS_REPORTED event is sent from "{sender}" with sourceCaseId')
def new_address_reported_event(context, sender):
    context.case_id = str(uuid.uuid4())
    context.collection_exercise_id = str(uuid.uuid4())
    context.sourceCaseId = str(context.case_created_events[0]['payload']['collectionCase']['id'])
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
                    "sourceCaseId": context.sourceCaseId,
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
                            "region": "E00001234",
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


@step('a NEW_ADDRESS_REPORTED event is sent from "{sender}" with sourceCaseId and minimal event fields')
def new_address_reported_event_with_minimal_fields(context, sender):
    context.case_id = str(uuid.uuid4())
    context.collection_exercise_id = str(uuid.uuid4())
    context.sourceCaseId = str(context.case_created_events[0]['payload']['collectionCase']['id'])
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
                    "sourceCaseId": context.sourceCaseId,
                    "collectionCase": {
                        "id": context.case_id,
                        "caseType": "SPG",
                        "address": {
                            "region": "E00001234",
                            "addressType": "SPG",
                            "addressLevel": "U"
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
    test_helper.assertEqual(context.first_case['collectionExerciseId'], context.collection_exercise_id)
    test_helper.assertEqual(context.first_case['addressLine1'], "123")
    test_helper.assertEqual(context.first_case['addressLine2'], "Fake caravan park")
    test_helper.assertEqual(context.first_case['addressLine3'], "The long road")
    test_helper.assertEqual(context.first_case['townName'], "Trumpton")
    test_helper.assertEqual(context.first_case['postcode'], "SO190PG")
    test_helper.assertEqual(context.first_case['region'], "E00001234")
    test_helper.assertEqual(context.first_case['addressType'], "SPG")
    test_helper.assertEqual(context.first_case['addressLevel'], "U")
    test_helper.assertEqual(context.first_case['latitude'], "50.917428")
    test_helper.assertEqual(context.first_case['longitude'], "-1.238193")
    test_helper.assertEqual(context.first_case['id'], context.case_id)


@step('the case can be retrieved and contains the correct properties when the event had details')
def retrieve_case(context):
    response = requests.get(f'{caseapi_url}{context.case_id}?caseEvents=true')
    test_helper.assertEqual(response.status_code, 200, 'Case not found')
    context.first_case = response.json()
    source_case = context.case_created_events[0]['payload']['collectionCase']

    test_helper.assertEqual(context.first_case['collectionExerciseId'], context.collection_exercise_id)
    test_helper.assertEqual(context.first_case['addressLine1'], "123")
    test_helper.assertEqual(context.first_case['addressLine2'], "Fake caravan park")
    test_helper.assertEqual(context.first_case['addressLine3'], "The long road")
    test_helper.assertEqual(context.first_case['townName'], "Trumpton")
    test_helper.assertEqual(context.first_case['postcode'], "SO190PG")
    test_helper.assertEqual(context.first_case['region'], "E00001234")
    test_helper.assertEqual(context.first_case['addressType'], "SPG")
    test_helper.assertEqual(context.first_case['addressLevel'], "U")
    test_helper.assertEqual(context.first_case['latitude'], "50.917428")
    test_helper.assertEqual(context.first_case['longitude'], "-1.238193")
    test_helper.assertEqual(context.first_case['id'], context.case_id)
    test_helper.assertEqual(context.first_case['estabUprn'], source_case['address']['estabUprn'])
    test_helper.assertEqual(context.first_case['lad'], source_case['lad'])
    test_helper.assertEqual(context.first_case['oa'], source_case['oa'])
    test_helper.assertEqual(context.first_case['msoa'], source_case['msoa'])
    test_helper.assertEqual(context.first_case['lsoa'], source_case['lsoa'])
    test_helper.assertEqual(context.first_case['organisationName'], source_case['address']['organisationName'])


@step('the case can be retrieved and contains the correct properties when the event had minimal details')
def retrieve_case(context):
    response = requests.get(f'{caseapi_url}{context.case_id}?caseEvents=true')
    test_helper.assertEqual(response.status_code, 200, 'Case not found')
    context.first_case = response.json()
    source_case = context.case_created_events[0]['payload']['collectionCase']

    test_helper.assertEqual(context.first_case['collectionExerciseId'], source_case['collectionExerciseId'])
    test_helper.assertEqual(context.first_case['addressLine1'], source_case['address']['addressLine1'])
    test_helper.assertEqual(context.first_case['addressLine2'], source_case['address']['addressLine2'])
    test_helper.assertEqual(context.first_case['addressLine3'], source_case['address']['addressLine3'])
    test_helper.assertEqual(context.first_case['townName'], source_case['address']['townName'])
    test_helper.assertEqual(context.first_case['postcode'], source_case['address']['postcode'])
    test_helper.assertEqual(context.first_case['region'], "E00001234")
    test_helper.assertEqual(context.first_case['addressType'], "SPG")
    test_helper.assertEqual(context.first_case['addressLevel'], "U")
    test_helper.assertEqual(context.first_case['latitude'], None)
    test_helper.assertEqual(context.first_case['longitude'], None)
    test_helper.assertEqual(context.first_case['id'], context.case_id)
    test_helper.assertEqual(context.first_case['estabUprn'], source_case['address']['estabUprn'])
    test_helper.assertEqual(context.first_case['lad'], source_case['lad'])
    test_helper.assertEqual(context.first_case['oa'], source_case['oa'])
    test_helper.assertEqual(context.first_case['msoa'], source_case['msoa'])
    test_helper.assertEqual(context.first_case['lsoa'], source_case['lsoa'])
    test_helper.assertEqual(context.first_case['organisationName'], source_case['address']['organisationName'])
    test_helper.assertEqual(context.first_case['uprn'], None)


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
                        "ceExpectedCapacity": "20",
                        "address": {
                            "organisationName": "bobs",
                            "uprn": "XXXXXXXXXXXXX",
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
            routing_key=Config.RABBITMQ_ADDRESS_ROUTING_KEY)


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
            routing_key=Config.RABBITMQ_ADDRESS_ROUTING_KEY)
