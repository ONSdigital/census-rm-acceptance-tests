import functools
import json
import logging

from behave import then
from retrying import retry
from structlog import wrap_logger

from acceptance_tests.utilities.print_file_helper import create_expected_csv_lines
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.sftp_utility import SftpUtility
from config import Config

logger = wrap_logger(logging.getLogger(__name__))


@then('messages are emitted to RH and Action Scheduler')
def gather_messages_emitted(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_QUEUE, functools.partial(_callback, context=context))


@then('correctly formatted print files are created')
def check_correct_files_on_sftp_server(context):
    expected_csv_lines = create_expected_csv_lines(context)
    _check_notification_files_have_all_the_expected_data(context, expected_csv_lines)


def _callback(ch, method, _properties, body, context):
    parsed_body = json.loads(body)
    context.messages_received.append(parsed_body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    if len(context.messages_received) == (len(context.sample_units) * 2):
        ch.stop_consuming()


def _check_notification_files_have_all_the_expected_data(context, expected_csv_lines):
    with SftpUtility() as sftp_utility:
        _validate_print_file_content(sftp_utility, context.test_start_local_datetime, expected_csv_lines)


@retry(retry_on_exception=lambda e: isinstance(e, FileNotFoundError), wait_fixed=5000, stop_max_attempt_number=24)
def _validate_print_file_content(sftp_utility, start_of_test, expected_csv_lines):
    logger.debug('Checking for files on SFTP server')

    files = sftp_utility.get_all_print_files_after_time(start_of_test)
    actual_content_list = sftp_utility.get_files_content_as_list(files)

    if set(actual_content_list) != set(expected_csv_lines):
        file_names = [f.filename for f in files]
        logger.info('Unable to find all expected data in existing files', files_found=file_names,
                    expected_csv_lines=expected_csv_lines, actual_content_list=actual_content_list)
        raise FileNotFoundError

    return True
