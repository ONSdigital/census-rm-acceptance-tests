import functools
import json
import uuid

import requests
from behave import step
from retrying import retry

from acceptance_tests.features.steps.unaddressed import get_case_id_by_questionnaire_id
from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context, \
    check_no_msgs_sent_to_queue
from acceptance_tests.utilities.string_utilities import create_random_postcode
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

caseapi_url = f'{Config.CASEAPI_SERVICE}/cases/'


@step("a CCS Property Listed event is sent")
def send_ccs_property_listed_event(context):
    message = _create_ccs_property_listed_event(context)
    _send_ccs_case_list_msg_to_rabbit(message)


@step("a CCS Property Listed event is sent with a qid")
def send_ccs_property_listed_event_with_qid(context):
    message = _create_ccs_property_listed_event(context)
    message['payload']['CCSProperty']['uac'] = [{
        "questionnaireId": context.expected_questionnaire_id
    }]

    _send_ccs_case_list_msg_to_rabbit(message)


@step('a CCS Property Listed event is sent with refusal')
def send_ccs_property_listed_event_with_refusal(context):
    message = _create_ccs_property_listed_event(context)
    message['payload']['CCSProperty']['refusal'] = {
        "type": "HARD_REFUSAL",
        "report": "respondent too busy",
        "agentId": "110001"
    }

    _send_ccs_case_list_msg_to_rabbit(message)


@step('a CCS Property Listed event is sent with an address invalid event and address type "{address_type}"')
def send_ccs_property_listed_event_with_invalid_address(context, address_type):
    message = _create_ccs_property_listed_event(context, address_type)
    message['payload']['CCSProperty']['invalidAddress'] = {
        "reason": "NON_RESIDENTIAL"
    }

    _send_ccs_case_list_msg_to_rabbit(message)


def _create_ccs_property_listed_event(context, address_type="HH"):
    context.case_id = str(uuid.uuid4())

    message = {
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
                    "addressType": address_type,
                    "estabType": "Household",
                    "addressLevel": "U",
                    "organisationName": "Testy McTest",
                    "addressLine1": "123 Fake street",
                    "addressLine2": "Upper upperingham",
                    "addressLine3": "Newport",
                    "townName": "upton",
                    "postcode": create_random_postcode(),
                    "latitude": "50.863849",
                    "longitude": "-1.229714",
                    "fieldCoordinatorId": "XXXXXXXXXX",
                    "fieldOfficerId": "XXXXXXXXXXXXX"
                },
            }
        }
    }

    return message


def _send_ccs_case_list_msg_to_rabbit(message):
    json_message = json.dumps(message)

    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=json_message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_CCS_PROPERTY_LISTING_ROUTING_KEY)


@step('the CCS Property Listed case is created with address type "{address_type}"')
@retry(stop_max_attempt_number=10, wait_fixed=1000)
def check_case_created(context, address_type):
    response = requests.get(f'{caseapi_url}{context.case_id}', params={'caseEvents': True})
    test_helper.assertEqual(response.status_code, 200, 'CCS Property Listed case not found')

    context.ccs_case = response.json()
    test_helper.assertEqual(context.ccs_case['addressType'], address_type)


@step("the correct ActionInstruction is sent to FWMT")
def check_correct_ccs_actioninstruction_sent_to_fwmt(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE,
                                    functools.partial(
                                        field_callback, context=context))

    action_instruction = context.emitted_action_instruction

    test_helper.assertEqual(context.ccs_case['id'], action_instruction['caseId'])
    test_helper.assertEqual(float(context.ccs_case['latitude']), action_instruction['latitude'])
    test_helper.assertEqual(float(context.ccs_case['longitude']), action_instruction['longitude'])
    test_helper.assertEqual(context.ccs_case['postcode'], action_instruction['postcode'])
    test_helper.assertEqual('CCS', action_instruction['surveyName'])
    test_helper.assertEqual(context.ccs_case['estabType'], action_instruction['estabType'])


def field_callback(ch, method, _properties, body, context):
    context.emitted_action_instruction = json.loads(body)

    if not context.emitted_action_instruction['actionInstruction'] == 'CREATE':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        test_helper.fail(f'Unexpected message on {Config.RABBITMQ_OUTBOUND_FIELD_QUEUE} case queue. '
                         f'Got "{context.emitted_action_instruction["actionInstruction"]}", wanted "CREATE"')

    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()


@step("no ActionInstruction is sent to FWMT")
def check_no_msg_sent_fwmt(context):
    check_no_msgs_sent_to_queue(context, Config.RABBITMQ_OUTBOUND_FIELD_QUEUE, functools.partial(
        store_all_msgs_in_context, context=context,
        expected_msg_count=0))


@step("the CCS case listed event is logged")
def ccs_case_event_logged(context):
    # currently no way of testing refusal set so just test event logged and didn't break anything
    test_helper.assertEqual(context.ccs_case['caseEvents'][0]['eventType'], 'CCS_ADDRESS_LISTED')


@step("the CCS Case created is set against the correct qid")
def check_created_uacqid_link_has_new_ccs_against_it(context):
    linked_ccs_case_id = get_case_id_by_questionnaire_id(context)
    test_helper.assertEqual(linked_ccs_case_id, context.case_id)
