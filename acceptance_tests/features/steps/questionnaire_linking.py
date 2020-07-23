import json
import time
import uuid

import requests
from behave.step_registry import step
from retrying import retry

from acceptance_tests.utilities.event_helper import get_uac_updated_events
from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.test_case_helper import test_helper
from acceptance_tests.utilities.unadressed_helper import send_questionnaire_linked_msg_to_rabbit
from config import Config


@step('a Questionnaire Linked message is sent for every requested qid')
def send_link_message_for_every_requested_unlinked_uac(context):
    for uac in context.unlinked_uacs:
        send_questionnaire_linked_msg_to_rabbit(uac['payload']['uac']['questionnaireId'], context.first_case['id'])


@step('a UAC updated event is emitted for every QID linking them to the case')
def check_linking_uac_update_event_is_emitted_for_all_unlinked_uacs(context):
    uac_updated_events = get_uac_updated_events(context, len(context.unlinked_uacs))
    for uac_updated_event in uac_updated_events:
        test_helper.assertEqual(uac_updated_event['payload']['uac']['caseId'], context.first_case['id'],
                                msg='UAC Updated message found with unexpected case ID')
    unlinked_qids = set(uac['payload']['uac']['questionnaireId'] for uac in context.unlinked_uacs)
    qid_links = set(uac['payload']['uac']['questionnaireId'] for uac in uac_updated_events)
    test_helper.assertSetEqual(unlinked_qids, qid_links,
                               msg='Should find UAC Updated messages linked every QID requested')


@step("a Questionnaire Linked message is sent")
def send_linked_message(context):
    send_questionnaire_link(context)
    context.linked_case_id = context.linked_case['id']


@step("a Questionnaire Linked message is sent to relink to a new case")
def send_linked_message_for_alternative_case(context):
    send_alternative_questionnaire_link(context)
    time.sleep(1)


@step("a Questionnaire Linked message is sent for blank questionnaire")
def send_linked_message_for_blank_questionnaire(context):
    check_blank_link_message_is_received(context)
    context.linked_case_id = context.linked_case['id']


@step("an Individual Questionnaire Linked message is sent and ingested")
def send_individual_linked_message_and_verify_new_case(context):
    context.linked_case_id = send_questionnaire_link_for_individual_hh_case(context)
    get_case_id_by_questionnaire_id(context.expected_questionnaire_id)


@step("an Individual Questionnaire Linked message with no individual case ID is sent and ingested")
def send_individual_linked_message_without_individual_case_id_and_verify_new_case(context):
    send_questionnaire_link_for_individual_hh_case(context, include_individual_id=False)
    context.linked_case_id = context.individual_case_id = get_case_id_by_questionnaire_id(
        context.expected_questionnaire_id)


@step("a Questionnaire Linked message is sent for the CCS case")
def send_ccs_linked_message(context):
    context.linked_case_id = context.case_id
    context.linked_uac = context.expected_uac

    send_questionnaire_linked_msg_to_rabbit(context.expected_questionnaire_id, context.linked_case_id)


def send_questionnaire_link(context):
    context.linked_case = context.first_case

    send_questionnaire_linked_msg_to_rabbit(context.expected_questionnaire_id, context.linked_case['id'])


def send_questionnaire_link_for_individual_hh_case(context, include_individual_id=True):
    context.linked_case = context.first_case
    if include_individual_id:
        context.individual_case_id = uuid.uuid4()
        _send_individual_hh_questionnaire_linked_msg_to_rabbit(context.expected_questionnaire_id,
                                                               context.linked_case['id'],
                                                               context.individual_case_id)
        return context.individual_case_id
    _send_individual_hh_questionnaire_linked_msg_to_rabbit(context.expected_questionnaire_id,
                                                           context.linked_case['id'])


def send_alternative_questionnaire_link(context):
    alternative_case = context.case_created_events[1]['payload']['collectionCase']

    context.linked_case_id = alternative_case['id']
    send_questionnaire_linked_msg_to_rabbit(context.expected_questionnaire_id, alternative_case['id'])


def check_blank_link_message_is_received(context):
    context.linked_case = context.case_created_events[0]['payload']['collectionCase']

    send_questionnaire_linked_msg_to_rabbit(context.expected_questionnaire_id, context.linked_case['id'])


@step("a Questionnaire Linked event is logged")
def check_questionnaire_linked_logging(context):
    check_question_linked_event_is_logged(context.linked_case_id)


@step("a Questionnaire Linked event on the parent case is logged")
def check_questionnaire_linked_logging_on_parent(context):
    check_question_linked_event_is_logged(context.linked_case['id'])


@step("a Questionnaire Unlinked event is logged")
def check_questionnaire_unlinked_logging(context):
    context.linked_case_id = context.first_case['id']
    check_question_unlinked_event_is_logged(context)


@retry(stop_max_attempt_number=10, wait_fixed=1000)
def check_question_linked_event_is_logged(case_id):
    response = requests.get(f'{Config.CASE_API_CASE_URL}{case_id}', params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        if case_event['description'] == 'Questionnaire Linked':
            return
    test_helper.fail('Did not find questionnaire linked event')


@retry(stop_max_attempt_number=10, wait_fixed=1000)
def check_question_unlinked_event_is_logged(context):
    case_id = context.linked_case_id
    response = requests.get(f'{Config.CASE_API_CASE_URL}{case_id}', params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        expected_desc = f'Questionnaire unlinked from case with QID {context.expected_questionnaire_id}'
        if case_event['description'] == expected_desc:
            return
    test_helper.fail('Questionnaire unlinked event has not occurred')


@retry(stop_max_attempt_number=10, wait_fixed=1000)
def get_case_id_by_questionnaire_id(questionnaire_id):
    response = requests.get(f'{Config.CASE_API_CASE_URL}/qid/{questionnaire_id}')
    test_helper.assertEqual(response.status_code, 200, "Unexpected status code")
    response_json = response.json()
    return response_json['id']


@step("the HI individual case can be retrieved")
def retrieve_hi_case(context):
    response = requests.get(f'{Config.CASE_API_CASE_URL}{context.individual_case_id}')
    test_helper.assertEqual(response.status_code, 200, 'Case not found')


def _send_individual_hh_questionnaire_linked_msg_to_rabbit(questionnaire_id, case_id, individual_case_id=None):
    questionnaire_linked_message = {
        'event': {
            'type': 'QUESTIONNAIRE_LINKED',
            'source': 'FIELDWORK_GATEWAY',
            'channel': 'FIELD',
            "dateTime": "2011-08-12T20:17:46.384Z",
            "transactionId": "c45de4dc-3c3b-11e9-b210-d663bd873d93"
        },
        'payload': {
            'uac': {
                "caseId": case_id,
                'questionnaireId': questionnaire_id,
            }
        }
    }
    if individual_case_id:
        questionnaire_linked_message['payload']['uac']['individualCaseId'] = str(individual_case_id)
    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=json.dumps(questionnaire_linked_message),
            content_type='application/json',
            routing_key=Config.RABBITMQ_QUESTIONNAIRE_LINKED_ROUTING_KEY)
