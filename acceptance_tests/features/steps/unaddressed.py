import functools
import json
import logging
import subprocess
import time
import urllib
import uuid

import requests
from behave import when, step, then
from requests.auth import HTTPBasicAuth
from retrying import retry
from structlog import wrap_logger

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

logger = wrap_logger(logging.getLogger(__name__))

caseapi_url = f'{Config.CASEAPI_SERVICE}/cases/'


@step('an unaddressed QID request message of questionnaire type {questionnaire_type} is sent')
def send_unaddressed_message(context, questionnaire_type):
    context.expected_questionnaire_type = questionnaire_type
    with RabbitContext(queue_name=Config.RABBITMQ_UNADDRESSED_REQUEST_QUEUE) as rabbit:
        rabbit.publish_message(
            message=json.dumps({'questionnaireType': questionnaire_type}),
            content_type='application/json')


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
    time.sleep(1)
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

    _send_questionnaire_linked_msg_to_rabbit(context.expected_questionnaire_id, context.linked_case_id)


def send_questionnaire_link(context):
    context.linked_case = context.case_created_events[1]['payload']['collectionCase']

    _send_questionnaire_linked_msg_to_rabbit(context.expected_questionnaire_id, context.linked_case['id'])


def send_questionnaire_link_for_individual_hh_case(context, include_individual_id=True):
    context.linked_case = context.case_created_events[1]['payload']['collectionCase']
    if include_individual_id:
        context.individual_case_id = uuid.uuid4()
        _send_individual_hh_questionnaire_linked_msg_to_rabbit(context.expected_questionnaire_id,
                                                               context.linked_case['id'],
                                                               context.individual_case_id)
        return context.individual_case_id
    _send_individual_hh_questionnaire_linked_msg_to_rabbit(context.expected_questionnaire_id,
                                                           context.linked_case['id'])


def send_alternative_questionnaire_link(context):
    alternative_case = context.case_created_events[0]['payload']['collectionCase']

    context.linked_case_id = alternative_case['id']
    _send_questionnaire_linked_msg_to_rabbit(context.expected_questionnaire_id, alternative_case['id'])


def check_blank_link_message_is_received(context):
    context.linked_case = context.case_created_events[0]['payload']['collectionCase']

    _send_questionnaire_linked_msg_to_rabbit(context.expected_questionnaire_id, context.linked_case['id'])


@step("a UACUpdated message not linked to a case is emitted to RH and Action Scheduler")
def check_uac_message_is_received(context):
    context.expected_message_received = False
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(_uac_callback, context=context))

    test_helper.assertTrue(context.expected_message_received)


@step("a Questionnaire Linked event is logged")
def check_questionnaire_linked_logging(context):
    check_question_linked_event_is_logged(context.linked_case_id)


@step("a Questionnaire Linked event on the parent case is logged")
def check_questionnaire_linked_logging_on_parent(context):
    check_question_linked_event_is_logged(context.linked_case['id'])


@step("a Questionnaire Unlinked event is logged")
def check_questionnaire_unlinked_logging(context):
    context.linked_case_id = context.case_created_events[1]['payload']['collectionCase']['id']
    check_question_unlinked_event_is_logged(context)


@retry(stop_max_attempt_number=10, wait_fixed=1000)
def check_question_linked_event_is_logged(case_id):
    response = requests.get(f'{caseapi_url}{case_id}', params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        if case_event['description'] == 'Questionnaire Linked':
            return
    test_helper.fail('Did not find questionnaire linked event')


@retry(stop_max_attempt_number=10, wait_fixed=1000)
def check_question_unlinked_event_is_logged(context):
    case_id = context.linked_case_id
    response = requests.get(f'{caseapi_url}{case_id}', params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        expected_desc = f'Questionnaire unlinked from case with QID {context.expected_questionnaire_id}'
        if case_event['description'] == expected_desc:
            return
    test_helper.fail('Questionnaire unlinked event has not occurred')


@retry(stop_max_attempt_number=10, wait_fixed=1000)
def get_case_id_by_questionnaire_id(questionnaire_id):
    response = requests.get(f'{caseapi_url}/qid/{questionnaire_id}')
    test_helper.assertEqual(response.status_code, 200, "Unexpected status code")
    response_json = response.json()
    return response_json['id']


def _uac_callback(ch, method, _properties, body, context):
    parsed_body = json.loads(body)

    if not parsed_body['event']['type'] == 'UAC_UPDATED':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        return

    test_helper.assertEqual(64, len(parsed_body['payload']['uac']['uacHash']))
    context.expected_questionnaire_id = parsed_body['payload']['uac']['questionnaireId']
    test_helper.assertEqual(context.expected_questionnaire_type, context.expected_questionnaire_id[:2])
    context.expected_uac = parsed_body['payload']['uac']['uac']
    context.expected_message_received = True
    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()


@when("the unaddressed batch is loaded, the print files are generated")
def validate_unaddressed_print_file(context):
    try:
        subprocess.run(
            ['docker', 'run',
             '--env', 'DB_HOST=postgres',
             '--env', 'DB_PORT=5432',
             '--env', 'OUR_PUBLIC_KEY_PATH=dummy_keys/our_dummy_public.asc',
             '--env', 'QM_PUBLIC_KEY_PATH=dummy_keys/supplier_QM_dummy_public_key.asc',
             '--env', 'PPO_PUBLIC_KEY_PATH=dummy_keys/supplier_PPO_dummy_public_key.asc',
             '--env', 'RABBITMQ_SERVICE_HOST=rabbitmq',
             '--env', 'RABBITMQ_SERVICE_PORT=5672',
             '--env', f'SFTP_QM_DIRECTORY={Config.SFTP_QM_DIRECTORY}',
             '--env', f'SFTP_PPO_DIRECTORY={Config.SFTP_PPO_DIRECTORY}',
             '--env', 'SFTP_HOST=sftp',
             '--env', 'SFTP_KEY_FILENAME=dummy_keys/dummy_rsa',
             '--env', 'SFTP_PASSPHRASE=secret',
             '--env', 'SFTP_USERNAME=centos',
             '--link', 'rabbitmq', '--link', 'postgres', '--network', 'censusrmdockerdev_default', '-t',
             'eu.gcr.io/census-rm-ci/rm/census-rm-qid-batch-runner', '/home/qidbatchrunner/run_acceptance_tests.sh'],
            check=True)
    except subprocess.CalledProcessError:
        test_helper.fail('Unaddressed print file test failed')


@then("message redelivery does not go bananas")
def check_message_redelivery_rate(context):
    time.sleep(2)  # Wait a couple of seconds for all hell to break loose

    v_host = urllib.parse.quote(Config.RABBITMQ_VHOST, safe='')
    response = requests.get(
        f'http://{Config.RABBITMQ_HOST}:{Config.RABBITMQ_HTTP_PORT}/api/queues/{v_host}/Case.Responses',
        auth=HTTPBasicAuth(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD))

    response.raise_for_status()
    queue_details = response.json()
    redeliver_rate = queue_details.get('message_stats', {}).get('redeliver_details', {}).get('rate')
    test_helper.assertFalse(redeliver_rate, "Redeliver rate should be zero")

    response = requests.get(
        f'http://{Config.RABBITMQ_HOST}:{Config.RABBITMQ_HTTP_PORT}/api/queues/{v_host}/FieldworkAdapter.caseUpdated',
        auth=HTTPBasicAuth(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD))

    response.raise_for_status()
    queue_details = response.json()
    redeliver_rate = queue_details.get('message_stats', {}).get('redeliver_details', {}).get('rate')

    test_helper.assertFalse(redeliver_rate, "Redeliver rate should be zero")


@step("the HI individual case can be retrieved")
def retrieve_hi_case(context):
    response = requests.get(f'{caseapi_url}{context.individual_case_id}')
    test_helper.assertEqual(response.status_code, 200, 'Case not found')


def _send_questionnaire_linked_msg_to_rabbit(questionnaire_id, case_id):
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
    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=json.dumps(questionnaire_linked_message),
            content_type='application/json',
            routing_key=Config.RABBITMQ_QUESTIONNAIRE_LINKED_ROUTING_KEY)


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
