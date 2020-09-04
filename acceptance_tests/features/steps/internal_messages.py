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
