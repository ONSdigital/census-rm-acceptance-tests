import functools
import hashlib
import json
import logging

from behave import then
from retrying import retry
from structlog import wrap_logger
from acceptance_tests.utilities.print_file_helper import create_expected_questionaire_csv_lines, \
    create_expected_csv_lines
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.sftp_utility import SftpUtility
from acceptance_tests.utilities.test_case_helper import tc
from config import Config

logger = wrap_logger(logging.getLogger(__name__))


@then('messages are emitted to RH and Action Scheduler')
def gather_messages_emitted(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                                    functools.partial(_callback, context=context))

    # the case created events have been received and we are now expecting the same number of uacupdated events (2x)
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(_callback, context=context, multiplier=2))


@then('messages are emitted to RH and Action Scheduler for wales questionnaire')
def gather_messages_emitted_wales(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                                    functools.partial(_callback, context=context))

    # for Welsh questionnaires there are 2 uac_created events plus a case created event
    # so there are 3 events in total
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(_callback, context=context, multiplier=3))


@then('messages are emitted to RH and Action Scheduler for questionnaire')
def gather_messages_emitted_questionair(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                                    functools.partial(_callback, context=context))

    # for non Welsh questionnaires there are 1 uac_created events plus a case created event
    # so there are 2 events in total
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(_callback, context=context, multiplier=2))


@then('correctly formatted "{prefix}" print files are created for questionnaire')
def check_correct_wales_files_on_sftp_server(context, prefix):
    expected_csv_lines = create_expected_questionaire_csv_lines(context, prefix)
    _check_notification_files_have_all_the_expected_data(context, expected_csv_lines, prefix)


@then('correctly formatted "{prefix}" print files are created')
def check_correct_files_on_sftp_server(context, prefix):
    expected_csv_lines = create_expected_csv_lines(context, prefix)
    _check_notification_files_have_all_the_expected_data(context, expected_csv_lines, prefix)


def _callback(ch, method, _properties, body, context, multiplier=1):
    parsed_body = json.loads(body)
    context.messages_received.append(parsed_body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    if len(context.messages_received) == (len(context.sample_units) * multiplier):
        ch.stop_consuming()


@then('there is a correct "{prefix}" manifest file for each csv file written')
def check_manifest_files(context, prefix):
    logger.debug("checking manifest files exist for csv files")
    _check_manifest_files_created(context, prefix)


def _check_notification_files_have_all_the_expected_data(context, expected_csv_lines, prefix):
    with SftpUtility() as sftp_utility:
        _validate_print_file_content(sftp_utility, context.test_start_local_datetime, expected_csv_lines, prefix)


@retry(retry_on_exception=lambda e: isinstance(e, FileNotFoundError), wait_fixed=5000, stop_max_attempt_number=24)
def _validate_print_file_content(sftp_utility, start_of_test, expected_csv_lines, prefix):
    logger.debug('Checking for files on SFTP server')

    files = sftp_utility.get_all_files_after_time(start_of_test, prefix, ".csv")

    actual_content_list = sftp_utility.get_files_content_as_list(files)

    if set(actual_content_list) != set(expected_csv_lines):
        file_names = [f.filename for f in files]
        logger.info('Unable to find all expected data in existing files', files_found=file_names,
                    expected_csv_lines=expected_csv_lines, actual_content_list=actual_content_list)
        raise FileNotFoundError

    return True


def _check_manifest_files_created(context, prefix):
    with SftpUtility() as sftp_utility:
        files = sftp_utility.get_all_files_after_time(context.test_start_local_datetime, prefix)

        for _file in files:
            if _file.filename.endswith(".csv"):
                csv_file = _file
                manifest_file = _get_matching_manifest_file(csv_file.filename, files)

                if manifest_file is None:
                    assert False, f'Failed to find manifest file for {csv_file.filename}'

                actual_manifest = _get_actual_manifest(sftp_utility, manifest_file)
                creation_datetime = actual_manifest['manifestCreated']
                expected_manifest = _create_expected_manifest(sftp_utility, csv_file, creation_datetime, prefix)
                tc.assertDictEqual(actual_manifest, expected_manifest)


def _get_actual_manifest(sftp_utility, manifest_file):
    actual_manifest_json = sftp_utility.get_file_contents_as_string(f'{Config.SFTP_DIR}/{manifest_file.filename}')
    return json.loads(actual_manifest_json)


def _get_matching_manifest_file(filename, files):
    manifest_filename = filename.replace(".csv", ".manifest")

    for _file in files:
        if _file.filename == manifest_filename:
            return _file

    return None


def _create_expected_manifest(sftp_utility, csv_file, created_datetime, prefix):
    actual_file_contents = sftp_utility.get_file_contents_as_string(f'{Config.SFTP_DIR}/{csv_file.filename}')

    purpose, country = _get_country_and_purpose(prefix)

    md5_hash = hashlib.md5(actual_file_contents.encode('utf-8')).hexdigest()
    expected_size = sftp_utility.get_file_size(f'{Config.SFTP_DIR}/{csv_file.filename}')

    _file = dict(
        sizeBytes=expected_size,
        md5sum=md5_hash,
        relativePath='.\\',
        name=csv_file.filename
    )

    manifest = dict(
        schemaVersion=1,
        files=[_file],
        sourceName="ONS_RM",
        manifestCreated=created_datetime,
        description=f'{purpose} - {country}',
        dataset="PPD1.1",
        version=1
    )

    return manifest


def _get_country_and_purpose(prefix):
    if "P_IC_ICL1" in prefix:
        country = 'England'
        purpose = 'Initial contact letter households'

    if "P_IC_ICL2" in prefix:
        country = 'Wales'
        purpose = 'Initial contact letter households'

    if "P_IC_ICL4" in prefix:
        country = 'Northern Ireland'
        purpose = 'Initial contact letter households'

    if "P_IC_H1" in prefix:
        country = "England"
        purpose = 'Initial contact questionnaire households'

    if "P_IC_H2" in prefix:
        country = 'Wales'
        purpose = 'Initial contact questionnaire households'

    if "P_IC_H4" in prefix:
        country = "Northern Ireland"
        purpose = 'Initial contact questionnaire households'

    return purpose, country
