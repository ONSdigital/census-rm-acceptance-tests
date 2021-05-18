import json
import logging
import subprocess

from behave import when, step
from structlog import wrap_logger

from acceptance_tests.utilities.mappings import QUESTIONNAIRE_TYPE_TO_FORM_TYPE
from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.test_case_helper import test_helper
from acceptance_tests.utilities.unadressed_helper import check_uac_message_is_received
from config import Config

logger = wrap_logger(logging.getLogger(__name__))


@step('an unaddressed QID request message of questionnaire type {questionnaire_type} is sent')
def send_unaddressed_message(context, questionnaire_type):
    context.expected_questionnaire_type = questionnaire_type
    with RabbitContext(queue_name=Config.RABBITMQ_UNADDRESSED_REQUEST_QUEUE) as rabbit:
        rabbit.publish_message(
            message=json.dumps({'questionnaireType': questionnaire_type}),
            content_type='application/json')


@step('an unaddressed QID request message of questionnaire type {questionnaire_type} is sent and an unlinked uac is '
      'emitted')
@step('an unaddressed QID request message of questionnaire type {questionnaire_type} is sent and an UAC msg is emitted')
def send_unaddressed_message_and_uac_emitted(context, questionnaire_type):
    send_unaddressed_message(context, questionnaire_type)
    check_uac_message_is_received(context)


@step('unaddressed QID request messages for every non-individual type census type are sent '
      'and an unlinked uacs are emitted')
def send_requests_for_every_non_individual_census_qid_type(context):
    context.messages_received = []
    for qid_type in [qid_type for qid_type, form_type in QUESTIONNAIRE_TYPE_TO_FORM_TYPE.items() if form_type != 'I']:
        send_unaddressed_message_and_uac_emitted(context, qid_type)
    context.unlinked_uacs = context.messages_received.copy()
    context.messages_received = []


@step('unaddressed QID request messages for every individual type census type are sent '
      'and an unlinked uacs are emitted')
def send_requests_for_every_individual_census_qid_type(context):
    context.messages_received = []
    for qid_type in [qid_type for qid_type, form_type in QUESTIONNAIRE_TYPE_TO_FORM_TYPE.items() if form_type == 'I']:
        send_unaddressed_message_and_uac_emitted(context, qid_type)
    context.unlinked_uacs = context.messages_received.copy()
    context.messages_received = []


@step("a UACUpdated message not linked to a case is emitted to RH and Action Scheduler")
def check_uac_message_is_received_step(context):
    check_uac_message_is_received(context)


@step('an unaddressed QID request message of type "{qid_type}" is received for every loaded case '
      'and resulting unlinked UAC_UPDATED message are sent')
def send_unaddressed_qid_request_for_every_case(context, qid_type):
    context.unlinked_uacs = []
    for _ in context.case_created_events:
        send_unaddressed_message_and_uac_emitted(context, qid_type)
        context.unlinked_uacs.append(context.uac_message_received)


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
