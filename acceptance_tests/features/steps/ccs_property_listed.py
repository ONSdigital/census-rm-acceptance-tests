import functools
import json
import uuid

import xml.etree.ElementTree as ET
import requests
from behave import step, then
from retrying import retry

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context, \
    check_no_msgs_sent_to_queue
from acceptance_tests.utilities.test_case_helper import test_helper
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
                    "addressType": "HH",
                    "estabType": "Household",
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
                }
            }
        }
    })

    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_CCS_PROPERTY_LISTING_ROUTING_KEY)


@step("a CCS Property Listed event is sent with a qid")
def send_ccs_property_listed_event_with_qid(context):
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
                    "addressType": "HH",
                    "estabType": "Household",
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
                    "questionnaireId": context.expected_questionnaire_id
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

    context.ccs_case = response.json()
    assert context.ccs_case['caseType'] == 'HH'  # caseType is derived from addressType for CCS


@then("the correct ActionInstruction is sent to FWMT")
def check_correct_ccs_actioninstruction_sent_to_fwmt(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE_TEST,
                                    functools.partial(
                                        field_callback, context=context))

    action_instruction = context.emitted_action_instruction

    test_helper.assertEqual(context.ccs_case['id'], action_instruction.find('.//caseId').text)
    test_helper.assertEqual(context.ccs_case['latitude'], action_instruction.find('.//latitude').text)
    test_helper.assertEqual(context.ccs_case['longitude'], action_instruction.find('.//longitude').text)
    test_helper.assertEqual(context.ccs_case['postcode'], action_instruction.find('.//postcode').text)
    test_helper.assertEqual('false', action_instruction.find('.//undeliveredAsAddress').text)
    test_helper.assertEqual('false', action_instruction.find('.//blankQreReturned').text)
    test_helper.assertEqual('CCS', action_instruction.find('.//surveyName').text)
    test_helper.assertEqual(context.ccs_case['estabType'], action_instruction.find('.//estabType').text)


def field_callback(ch, method, _properties, body, context):
    context.emitted_action_instruction = ET.fromstring(body)

    if not context.emitted_action_instruction[0].tag == 'actionRequest':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        test_helper.fail('Unexpected message on Action.Field case queue')

    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()


@then("no ActionInstruction is sent to FWMT")
def check_no_msg_sent_fwmt(context):
    check_no_msgs_sent_to_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE_TEST,
                                functools.partial(
                                    store_all_msgs_in_context, context=context,
                                    expected_msg_count=0))
