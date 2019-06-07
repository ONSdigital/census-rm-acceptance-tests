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


@then("messages are emitted to RH and Action Scheduler for with {qid_count} qid per sample")
def gather_messages_emitted(context, qid_count):
    context.expected_sample_units = context.sample_units.copy()
    context.messages_received = []
    context.case_created_events = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST,
                                    functools.partial(_cases_callback, context=context))

    # by multipler add case_created_events to itself i.e. 2 for Wales
    events_copy = context.case_created_events.copy()
    for x in range(1, int(qid_count)):
        context.case_created_events.extend(events_copy)

    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(_uac_callback, context=context))


def _cases_callback(ch, method, _properties, body, context):
    parsed_body = json.loads(body)

    if not parsed_body['event']['type'] == 'CASE_CREATED':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        assert False, 'Unexpected message on RH case queue'
        return

    _validate_message(parsed_body)

    for index, sample_unit in enumerate(context.expected_sample_units):
        if _sample_matches_rh_message(sample_unit, parsed_body):
            context.messages_received.append(parsed_body)
            context.case_created_events.append(parsed_body
                                               )
            del context.expected_sample_units[index]
            ch.basic_ack(delivery_tag=method.delivery_tag)
            break
    else:
        assert False, 'Could not find sample unit'

    if not context.expected_sample_units:
        ch.stop_consuming()


def _sample_matches_rh_message(sample_unit, rh_message):
    return sample_unit['attributes']['ADDRESS_LINE1'] == \
           rh_message['payload']['collectionCase']['address']['addressLine1'] \
           and sample_unit['attributes']['ADDRESS_LINE2'] == \
           rh_message['payload']['collectionCase']['address']['addressLine2'] \
           and sample_unit['attributes']['REGION'][0] == rh_message['payload']['collectionCase']['address']['region']


def _uac_callback(ch, method, _properties, body, context):
    parsed_body = json.loads(body)

    t = parsed_body['event']['type']
    if not t == 'UAC_UPDATED':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        assert False, 'Unexpected message on RH UAC queue'
        return

    _validate_uac_message(parsed_body)

    for index, case_created_event in enumerate(context.case_created_events):
        if _uac_message_matches_rh_message(case_created_event, parsed_body):
            context.messages_received.append(parsed_body)
            del context.case_created_events[index]
            ch.basic_ack(delivery_tag=method.delivery_tag)
            break
    else:
        assert False, 'Could not find UAC Updated event'

    if not context.case_created_events:
        ch.stop_consuming()


def _validate_uac_message(parsed_body):
    tc.assertEqual(64, len(parsed_body['payload']['uac']['uacHash']))


def _uac_message_matches_rh_message(case_created_event, rh_message):
    return case_created_event['payload']['collectionCase']['id'] == rh_message['payload']['uac']['caseId']


def _validate_message(parsed_body):
    tc.assertEqual('CENSUS', parsed_body['payload']['collectionCase']['survey'])
    tc.assertEqual('ACTIONABLE', parsed_body['payload']['collectionCase']['state'])
    tc.assertEqual(8, len(parsed_body['payload']['collectionCase']['caseRef']))


@then('correctly formatted "{prefix}" print files are created for questionnaire')
def check_correct_wales_files_on_sftp_server(context, prefix):
    expected_csv_lines = create_expected_questionaire_csv_lines(context, prefix)
    _check_notification_files_have_all_the_expected_data(context, expected_csv_lines, prefix)


@then('correctly formatted "{prefix}" print files are created')
def check_correct_files_on_sftp_server(context, prefix):
    expected_csv_lines = create_expected_csv_lines(context, prefix)
    _check_notification_files_have_all_the_expected_data(context, expected_csv_lines, prefix)


def _msgs_received(ch, method, _properties, body, context, multiplier=1):
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


@retry(retry_on_exception=lambda e: isinstance(e, FileNotFoundError), wait_fixed=1000, stop_max_attempt_number=120)
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
    if "P_IC_ICL1" == prefix:
        return 'Initial contact letter households', 'England'

    if "P_IC_ICL2" == prefix:
        return 'Initial contact letter households', 'Wales'

    if "P_IC_ICL4" == prefix:
        return 'Initial contact letter households', 'Northern Ireland'

    if "P_IC_H1" == prefix:
        return 'Initial contact questionnaire households', 'England'

    if "P_IC_H2" == prefix:
        return 'Initial contact questionnaire households', 'Wales'

    if "P_IC_H4" == prefix:
        return 'Initial contact questionnaire households', 'Northern Ireland'

    assert False, f'Unexpected Prefix: {prefix}'
