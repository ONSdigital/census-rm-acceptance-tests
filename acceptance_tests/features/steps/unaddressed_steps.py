import csv
import functools
import json
from pathlib import Path
from uuid import uuid4

from behave import when, then, given

from acceptance_tests.utilities.qid_batch_runner.generate_print_files import generate_print_files_from_config_file_path, \
    PRINT_FILE_TEMPLATE
from acceptance_tests.utilities.qid_batch_runner.generate_qid_batch import generate_messages_from_config_file_path
from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import tc
from config import Config


@given("I have the QID and UAC pairs ready")
def generate_qid_uac_pairs(context):
    context.batch_id = uuid4()
    generate_messages_from_config_file_path(Path('resources/unaddressed_batch/unaddressed_batch.csv'),
                                            context.batch_id)
    context.message_count = 0
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(stop_consuming_after_n_messages, context=context, n=30))


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


def stop_consuming_after_n_messages(ch, method, _properties, _body, context, n):
    context.message_count += 1
    ch.basic_ack(delivery_tag=method.delivery_tag)
    if context.message_count >= n:
        ch.stop_consuming()


@when("the print files are generated")
def generate_print_files(context):
    context.print_file_paths = generate_print_files_from_config_file_path(
        Path('resources/unaddressed_batch/unaddressed_batch.csv'),  # TODO: use relative path
        context.test_file_path,
        context.batch_id)


@then("the print files contain the correct data")
def validate_print_file_data(context):
    manifests = [file_path for file_path in context.print_file_paths if file_path.suffix == '.manifest']
    print_files = [file_path for file_path in context.print_file_paths if file_path.suffix == '.csv']

    config_file = [("D_FD_H1", "01", "10"),
                   ("D_FD_H2", "02", "10"),
                   ("D_CCS_CH1", "71", "10")]

    assert len(manifests) == 3, 'Incorrect number of manifest files'

    for index, print_file in enumerate(print_files):
        with open(print_file) as fh:
            reader = csv.DictReader(fh, delimiter='|', fieldnames=PRINT_FILE_TEMPLATE)
            row_counter = 0
            for row in reader:
                row_counter += 1
                assert len(row['UAC']) == 16, 'Incorrect UAC length'
                assert row['PRODUCTPACK_CODE'] == config_file[index][0], 'PRODUCTPACK_CODE does not match config'
                assert row['QUESTIONNAIRE_ID'][:2] == config_file[index][1], 'QUESTIONNAIRE_ID does not match config'
            assert row_counter == int(config_file[index][2]), 'Print file row count does not match config'
