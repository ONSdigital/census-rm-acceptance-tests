import functools
import json
import logging
import subprocess

from behave import then, when
from structlog import wrap_logger

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import tc
from config import Config

logger = wrap_logger(logging.getLogger(__name__))


@when('an unaddressed message of questionnaire type {questionnaire_type} is sent')
def send_unaddressed_message(context, questionnaire_type):
    context.expected_questionnaire_type = questionnaire_type
    with RabbitContext(queue_name=Config.RABBITMQ_UNADDRESSED_REQUEST_QUEUE) as rabbit:
        rabbit.publish_message(
            message=json.dumps({'questionnaireType': questionnaire_type}),
            content_type='application/json')


@then("a UACUpdated message not linked to a case is emitted to RH and Action Scheduler")
def check_uac_message_is_received(context):
    context.expected_message_received = False
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(_uac_callback, context=context))

    assert context.expected_message_received


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


@when("the unaddressed batch is loaded, the print files are generated")
def validate_unaddressed_print_file(context):
    try:
        subprocess.run(
            ['docker', 'run',
             '--env', f'RABBITMQ_SERVICE_HOST=rabbitmq',
             '--env', f'RABBITMQ_SERVICE_PORT=5672',
             '--env', f'DB_PORT=5432',
             '--env', f'DB_HOST=postgres',
             '--link', 'rabbitmq', '--link', 'postgres', '--network', 'censusrmdockerdev_default', '-t',
             'eu.gcr.io/census-rm-ci/rm/census-rm-qid-batch-runner', '/app/run_acceptance_tests.sh'],
            check=True)
    except subprocess.CalledProcessError:
        raise AssertionError(f'Unaddressed print file test failed')
