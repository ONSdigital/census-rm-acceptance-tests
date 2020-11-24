import json
import uuid

from behave import step

from acceptance_tests.utilities.event_helper import get_case_updated_events
from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step("an RM address update message is sent")
def an_rm_address_update_message_is_sent(context):
    rm_case_updated = {
        "caseId": context.first_case['id'],
        "treatmentCode": "TEST TreatmentCode CODE",
        "estabType": "ROYAL HOUSEHOLD",
        "oa": "TEST Oa CODE",
        "lsoa": "TEST Lsoa CODE",
        "msoa": "TEST Msoa CODE",
        "lad": "TEST Lad CODE",
        "fieldCoordinatorId": "TEST FieldCoordinatorId CODE",
        "fieldOfficerId": "TEST FieldOfficerId CODE",
        "latitude": "123.456",
        "longitude": "000.000"
    }

    message = json.dumps({
        "event": {
            "type": "RM_CASE_UPDATED",
            "source": "ACCEPTANCE_TEST",
            "channel": "TEST",
            "dateTime": "2011-08-12T20:17:46.384Z",
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "rmCaseUpdated": rm_case_updated
        }
    })

    context.rm_case_updated = rm_case_updated

    with RabbitContext(exchange='') as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.BULK_ADDRESS_UPDATE_ROUTING_KEY)


@step('CASE_UPDATED event is emitted with updated case data')
def check_case_updated_event(context):
    context.case_updated_events = get_case_updated_events(context, 1)
    collection_case = context.case_updated_events[0]['payload']['collectionCase']

    test_helper.assertIn(collection_case['id'], context.rm_case_updated['caseId'])
    test_helper.assertEqual(collection_case['treatmentCode'], context.rm_case_updated['treatmentCode'])
    test_helper.assertEqual(collection_case['address']['estabType'], context.rm_case_updated['estabType'])
    test_helper.assertEqual(collection_case['oa'], context.rm_case_updated['oa'])
    test_helper.assertEqual(collection_case['lsoa'], context.rm_case_updated['lsoa'])
    test_helper.assertEqual(collection_case['msoa'], context.rm_case_updated['msoa'])
    test_helper.assertEqual(collection_case['lad'], context.rm_case_updated['lad'])
    test_helper.assertEqual(collection_case['fieldCoordinatorId'],
                            context.rm_case_updated['fieldCoordinatorId'])
    test_helper.assertEqual(collection_case['fieldOfficerId'], context.rm_case_updated['fieldOfficerId'])
    test_helper.assertEqual(collection_case['address']['latitude'], context.rm_case_updated['latitude'])
    test_helper.assertEqual(collection_case['address']['longitude'], context.rm_case_updated['longitude'])
    test_helper.assertFalse(collection_case['skeleton'], 'Skeleton flag should be removed from updated case')


@step("a deactivate uac msg is sent for each uac emitted")
def deactivate_uac_(context):
    context.bulk_deactivate_uac = []
    for uac_updated in context.uac_created_events:
        context.bulk_deactivate_uac.append(uac_updated['payload']['uac']['questionnaireId'])
        message = json.dumps(
            {
                "event": {
                    "type": "DEACTIVATE_UAC",
                    "source": "TESTY TEST",
                    "channel": "AR",
                    "dateTime": "2019-07-07T22:37:11.988+0000",
                    "transactionId": "d2541acb-230a-4ade-8123-eee2310c9143"
                },
                "payload": {
                    "uac": {
                        "questionnaireId": uac_updated['payload']['uac']['questionnaireId'],
                    }
                }
            }
        )

        with RabbitContext(exchange='') as rabbit:
            rabbit.publish_message(
                message=message,
                content_type='application/json',
                routing_key=Config.RABBITMQ_DEACTIVATE_UAC_QUEUE)


@step("an UNINVALIDATE_ADDRESS message is sent")
def uninvalidate_address(context):
    context.bulk_uninvalidated_addresses = []

    for invalid_address in context.case_created_events:
        invalid = {'CASE_ID': invalid_address['payload']['collectionCase']['id']}
        context.bulk_uninvalidated_addresses.append(invalid)
        message = json.dumps(
            {
                "event": {
                    "type": "RM_UNINVALIDATE_ADDRESS",
                    "source": "TESTY TEST",
                    "channel": "AR",
                    "dateTime": "2019-07-07T22:37:11.988+0000",
                    "transactionId": "d2541acb-230a-4ade-8123-eee2310c9143"
                },
                "payload": {
                    "rmUnInvalidateAddress": {
                        "caseId": invalid_address['payload']['collectionCase']['id']
                    }
                }
            }
        )

        with RabbitContext(exchange='') as rabbit:
            rabbit.publish_message(
                message=message,
                content_type='application/json',
                routing_key=Config.RABBITMQ_UNINVALIDATE_ADDRESS_QUEUE)


@step('CASE_UPDATED events are emitted for all the cases')
def check_address_valid_case_updated_events(context):
    address_valid_case_ids = [case_id['CASE_ID'] for case_id in context.bulk_uninvalidated_addresses]
    context.case_updated_events = get_case_updated_events(context, len(address_valid_case_ids))
    test_helper.assertEqual(len(context.case_updated_events), len(context.bulk_uninvalidated_addresses))
    for event in context.case_updated_events:
        test_helper.assertFalse(event['payload']['collectionCase']['addressInvalid'],
                                'Address invalid flag must be "False" on all updated events')
        test_helper.assertIn(event['payload']['collectionCase']['id'], address_valid_case_ids,
                             'Unexpected case ID found on updated event')


@step("a non compliance message is sent")
def non_compliance_msg_sent(context):
    context.non_compliance_case_id = context.case_created_events[0]['payload']['collectionCase']['id']

    message = json.dumps(
        {
            "event": {
                "type": "SELECTED_FOR_NON_COMPLIANCE",
                "source": "NON_COMPLIANCE",
                "channel": "NC",
                "dateTime": "2019-07-07T22:37:11.988+0000",
                "transactionId": "d2541acb-230a-4ade-8123-eee2310c9143"
            },
            "payload": {
                "collectionCase": {
                    "id": context.non_compliance_case_id,
                    "nonComplianceStatus": 'NCF',
                }
            }
        }
    )

    with RabbitContext(exchange='') as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_NONCOMPLIANCE_QUEUE)


@step("a case updated event is emitted with nonCompliance set")
def check_address_valid_case_updated_event_non_compliance(context):
    collection_case = get_case_updated_events(context, 1)[0]['payload']['collectionCase']

    test_helper.assertEqual(collection_case['id'], context.non_compliance_case_id)
    test_helper.assertEqual(collection_case['metadata']['nonCompliance'], 'NCF')
