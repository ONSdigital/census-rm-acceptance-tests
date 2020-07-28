import functools
import json
import uuid
from time import sleep

import requests
from behave import step

from acceptance_tests.utilities.event_helper import check_case_created_message_is_emitted
from acceptance_tests.utilities.pubsub_helper import sync_consume_of_pubsub,  \
    purge_aims_new_address_topic
from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


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
    response = requests.get(f"{Config.CASE_API_CASE_URL}{context.first_case['id']}", params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        if case_event['description'] == 'Invalid address':
            return
    test_helper.fail('Did not find expected invalid address event')


@step('a NEW_ADDRESS_REPORTED event is sent from "{sender}" without sourceCaseId')
def new_address_reported_event_without_source_case_id(context, sender):
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
                            "longitude": "-1.238193",
                            "uprn": None
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


@step(
    'a NEW_ADDRESS_REPORTED event is sent from "{sender}" without sourceCaseId with region "{region}", '
    'address type "{address_type}" and address level "{address_level}" and case emitted')
def new_address_reported_event_without_source_case_id_with_address_type(context, sender, region,
                                                                        address_type, address_level):
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
                        "caseType": address_type,
                        "survey": "CENSUS",
                        "fieldCoordinatorId": "SO_23",
                        "fieldOfficerId": "SO_23_123",
                        "collectionExerciseId": context.collection_exercise_id,
                        "address": {
                            "addressLine1": "123",
                            "addressLine2": "Fake caravan park",
                            "addressLine3": "The long road",
                            "townName": "Trumpton",
                            "postcode": "SO190PG",
                            "region": region,
                            "addressType": address_type,
                            "addressLevel": address_level,
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

    check_case_created_message_is_emitted(context)


@step('a NEW_ADDRESS_REPORTED event is sent from "{sender}" with sourceCaseId')
def new_address_reported_event_with_source_case_id(context, sender):
    context.case_id = str(uuid.uuid4())
    context.collection_exercise_id = str(uuid.uuid4())
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    context.sourceCaseId = str(context.first_case['id'])
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
                        "fieldCoordinatorId": "SO_23",
                        "fieldOfficerId": "SO_23_123",
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


@step('a NEW_ADDRESS_REPORTED event with address type "{address_type}" is sent from "{sender}" and the case is created')
def new_address_reported_event_for_address_type(context, address_type, sender):
    context.case_id = str(uuid.uuid4())
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
                    "collectionCase": {
                        "id": context.case_id,
                        "caseType": address_type,
                        "address": {
                            "region": "E00001234",
                            "addressType": address_type,
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

    check_case_created_message_is_emitted(context)


@step('a NEW_ADDRESS_REPORTED event with region "{region}", address type "{address_type}" and address level '
      '"{address_level}" is sent from "{sender}" and case emitted')
def new_address_reported_event_for_address_type_and_region(context, address_type, sender, address_level, region):
    context.case_id = str(uuid.uuid4())
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
                    "collectionCase": {
                        "id": context.case_id,
                        "caseType": address_type,
                        "address": {
                            "region": region,
                            "addressType": address_type,
                            "addressLevel": address_level
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

    check_case_created_message_is_emitted(context)


@step('the case can be retrieved')
def retrieve_skeleton_case(context):
    response = requests.get(f'{Config.CASE_API_CASE_URL}{context.case_id}?caseEvents=true')
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
def retrieve_case_from_source_case_id_and_event_details(context):
    response = requests.get(f'{Config.CASE_API_CASE_URL}{context.case_id}?caseEvents=true')
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
    test_helper.assertEqual(context.first_case['secureEstablishment'], source_case['metadata']['secureEstablishment'])


@step('the case can be retrieved and contains the correct properties when the event had minimal details')
def retrieve_case_from_source_case_id_and_no_event_details(context):
    response = requests.get(f'{Config.CASE_API_CASE_URL}{context.case_id}?caseEvents=true')
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
    test_helper.assertEqual(context.first_case['latitude'], source_case['address']['latitude'])
    test_helper.assertEqual(context.first_case['longitude'], source_case['address']['longitude'])
    test_helper.assertEqual(context.first_case['id'], context.case_id)
    test_helper.assertEqual(context.first_case['estabUprn'], source_case['address']['estabUprn'])
    test_helper.assertEqual(context.first_case['lad'], source_case['lad'])
    test_helper.assertEqual(context.first_case['oa'], source_case['oa'])
    test_helper.assertEqual(context.first_case['msoa'], source_case['msoa'])
    test_helper.assertEqual(context.first_case['lsoa'], source_case['lsoa'])
    test_helper.assertEqual(context.first_case['organisationName'], source_case['address']['organisationName'])
    test_helper.assertEqual(context.first_case['uprn'], f"999{context.first_case['caseRef']}")
    test_helper.assertEqual(context.first_case['secureEstablishment'], source_case['metadata']['secureEstablishment'])


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


@step("a CREATE action instruction is sent to field")
def create_msg_sent_to_field(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE, functools.partial(
        _field_work_create_callback, context=context))

    test_helper.assertEqual(context.fwmt_emitted_case_id, context.case_id)
    test_helper.assertEqual(context.addressType, "SPG")
    test_helper.assertEqual(context.field_action_cancel_message['surveyName'], "CENSUS")


@step('the action plan and collection exercises IDs are the hardcoded census values')
def use_census_action_plan_id(context):
    # For tests where the action plan and collection exercise ID need hardcoding
    # e.g where skeleton cases are used
    context.action_plan_id = Config.CENSUS_ACTION_PLAN_ID
    context.collection_exercise_id = Config.CENSUS_COLLECTION_EXERCISE_ID


def _field_work_create_callback(ch, method, _properties, body, context):
    action_create = json.loads(body)

    if not action_create['actionInstruction'] == 'CREATE':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        test_helper.fail(f'Unexpected message on {Config.RABBITMQ_OUTBOUND_FIELD_QUEUE} case queue. '
                         f'Got "{action_create["actionInstruction"]}", wanted "CREATE"')

    context.addressType = action_create['addressType']
    context.fwmt_emitted_case_id = action_create['caseId']
    context.field_action_cancel_message = action_create
    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()


@step('a NEW_ADDRESS_REPORTED event is sent from "{sender}" without sourceCaseId and new case is emitted')
def new_address_without_source_id(context, sender):
    new_address_reported_event_without_source_case_id(context, sender)
    check_case_created_message_is_emitted(context)


@step('a NEW_ADDRESS_REPORTED event is sent from "{sender}" without sourceCaseId or UPRN')
def step_impl(context, sender):
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
                            "longitude": "-1.238193",
                            "uprn": None
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


@step("a NEW_ADDRESS_ENHANCED event is sent to aims")
def new_address_sent_to_aims(context):
    sync_consume_of_pubsub(context)

    test_helper.assertEqual(context.aims_new_address_message['payload']['newAddress']['collectionCase']['id'],
                            context.case_id)
    test_helper.assertEqual(context.aims_new_address_message['event']['type'], 'NEW_ADDRESS_ENHANCED')
