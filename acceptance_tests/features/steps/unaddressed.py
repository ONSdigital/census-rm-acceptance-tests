import functools
import json
import logging
import subprocess
import time

import requests
from behave import then, when
from structlog import wrap_logger

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, purge_queues
from acceptance_tests.utilities.test_case_helper import tc
from config import Config

logger = wrap_logger(logging.getLogger(__name__))

caseapi_url = f'{Config.CASEAPI_SERVICE}/cases/'


@when('an unaddressed message of questionnaire type {questionnaire_type} is sent')
def send_unaddressed_message(context, questionnaire_type):
    context.expected_questionnaire_type = questionnaire_type
    with RabbitContext(queue_name=Config.RABBITMQ_UNADDRESSED_REQUEST_QUEUE) as rabbit:
        rabbit.publish_message(
            message=json.dumps({'questionnaireType': questionnaire_type}),
            content_type='application/json')


@when("a Questionnaire Linked message is sent")
def check_linked_message_is_received(context):
    # Delete receipt event
    purge_queues(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST)

    context.linked_case = context.case_created_events[0]['payload']['collectionCase']
    context.linked_uac = context.uac_created_events[0]['payload']['uac']

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
                "caseId": context.linked_case['id'],
                'questionnaireId': context.linked_uac['questionnaireId']
            }
        }
    }

    with RabbitContext(queue_name=Config.RABBITMQ_QUESTIONNAIRE_LINKED_QUEUE) as rabbit:
        rabbit.publish_message(
            message=json.dumps(questionnaire_linked_message),
            content_type='application/json')


@then("a UACUpdated message not linked to a case is emitted to RH and Action Scheduler")
def check_uac_message_is_received(context):
    context.expected_message_received = False
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(_uac_callback, context=context))

    assert context.expected_message_received


@then("a CaseUpdated message is emitted to RH and Action Scheduler")
def check_case_updated_message_is_emitted(context):
    context.expected_message_received = False
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST,
                                    functools.partial(_questionnaire_linked_callback, context=context))
    assert context.expected_message_received



@then("a Questionnaire Linked event is logged")
def check_case_events(context):
    context.linked_case_id = context.linked_case['id']
    time.sleep(2)  # Give case processor a chance to process the fulfilment request event
    response = requests.get(f'{caseapi_url}{context.linked_case_id}', params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        if case_event['description'] == 'Questionnaire Linked':
            return
    assert False


def _uac_callback(ch, method, _properties, body, context):
    parsed_body = json.loads(body)

    if not parsed_body['event']['type'] == 'UAC_UPDATED':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        return

    tc.assertEqual(64, len(parsed_body['payload']['uac']['uacHash']))
    tc.assertEqual(context.expected_questionnaire_type, parsed_body['payload']['uac']['questionnaireId'][:2])
    tc.assertIsNone(parsed_body['payload']['uac']['caseId'])
    context.expected_message_received = True
    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()


def _questionnaire_linked_callback(ch, method, _properties, body, context):
    parsed_body = json.loads(body)

    if not parsed_body['event']['type'] == 'CASE_UPDATED':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        return

    tc.assertEqual(context.linked_case_id, parsed_body['payload']['collectionCase']['id'])
    tc.assertEqual(True, parsed_body['payload']['collectionCase']['receiptReceived'])
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
             '--env', 'OTHER_PUBLIC_KEY_PATH=dummy_keys/supplier_dummy_public.asc',
             '--env', 'RABBITMQ_SERVICE_HOST=rabbitmq',
             '--env', 'RABBITMQ_SERVICE_PORT=5672',
             '--env', f'SFTP_DIRECTORY={Config.SFTP_QM_DIRECTORY}',
             '--env', 'SFTP_HOST=sftp',
             '--env', 'SFTP_KEY_FILENAME=dummy_keys/dummy_rsa',
             '--env', 'SFTP_PASSPHRASE=secret',
             '--env', 'SFTP_USERNAME=centos',
             '--link', 'rabbitmq', '--link', 'postgres', '--network', 'censusrmdockerdev_default', '-t',
             'eu.gcr.io/census-rm-ci/rm/census-rm-qid-batch-runner', '/app/run_acceptance_tests.sh'],
            check=True)
    except subprocess.CalledProcessError:
        raise AssertionError('Unaddressed print file test failed')
