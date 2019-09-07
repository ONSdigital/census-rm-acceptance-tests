import hashlib
import json
import logging

from behave import then, step
from retrying import retry
from structlog import wrap_logger

from acceptance_tests.utilities.mappings import PACK_CODE_TO_SFTP_DIRECTORY, PACK_CODE_TO_DATASET, \
    PACK_CODE_TO_DESCRIPTION
from acceptance_tests.utilities.print_file_helper import create_expected_questionnaire_csv_lines, \
    create_expected_csv_lines, create_expected_on_request_questionnaire_csv, \
    create_expected_supplementary_materials_csv, create_expected_reminder_letter_csv_lines, \
    create_expected_reminder_questionnaire_csv_lines
from acceptance_tests.utilities.sftp_utility import SftpUtility
from acceptance_tests.utilities.test_case_helper import test_helper

logger = wrap_logger(logging.getLogger(__name__))


@then('correctly formatted "{pack_code}" print files are created for questionnaire')
def check_correct_questionnaire_files_on_sftp_server(context, pack_code):
    expected_csv_lines = create_expected_questionnaire_csv_lines(context, pack_code)
    _check_print_files_have_all_the_expected_data(context, expected_csv_lines, pack_code)


@then('correctly formatted "{pack_code}" print files are created')
def check_correct_files_on_sftp_server(context, pack_code):
    expected_csv_lines = create_expected_csv_lines(context, pack_code)
    _check_print_files_have_all_the_expected_data(context, expected_csv_lines, pack_code)


@then('correctly formatted "{pack_code}" reminder letter print files are created')
def check_correct_reminder_letter_files_on_sftp_server(context, pack_code):
    expected_csv_lines = create_expected_reminder_letter_csv_lines(context, pack_code)
    _check_print_files_have_all_the_expected_data(context, expected_csv_lines, pack_code)


@then('correctly formatted "{pack_code}" reminder questionnaire print files are created')
def check_correct_reminder_questionnaire_files_on_sftp_server(context, pack_code):
    expected_csv_lines = create_expected_reminder_questionnaire_csv_lines(context, pack_code)
    _check_print_files_have_all_the_expected_data(context, expected_csv_lines, pack_code)


@then('only unrefused cases appear in "{pack_code}" print files')
def check_correct_unrefused_files_on_sftp_server(context, pack_code):
    expected_csv_lines = create_expected_csv_lines(context, pack_code, context.refused_case_id)
    _check_print_files_have_all_the_expected_data(context, expected_csv_lines, pack_code)


@then('only unreceipted cases appear in "{pack_code}" print files')
def check_correct_unreceipted_files_on_sftp_server(context, pack_code):
    expected_csv_lines = create_expected_csv_lines(context, pack_code, context.emitted_case['id'])
    _check_print_files_have_all_the_expected_data(context, expected_csv_lines, pack_code)


def _msgs_received(ch, method, _properties, body, context, multiplier=1):
    parsed_body = json.loads(body)
    context.messages_received.append(parsed_body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    if len(context.messages_received) == (len(context.sample_units) * multiplier):
        ch.stop_consuming()


@then('there is a correct "{pack_code}" manifest file for each csv file written')
def check_manifest_files(context, pack_code):
    logger.debug("checking manifest files exist for csv files")
    _check_manifest_files_created(context, pack_code)


@step('correctly formatted on request contn questionnaire print and manifest files for "{fulfilment_code}" are created')
@step('correctly formatted on request questionnaire print and manifest files for "{fulfilment_code}" are created')
def correct_on_request_questionnaire_print_files(context, fulfilment_code):
    expected_csv_lines = create_expected_on_request_questionnaire_csv(context, fulfilment_code)
    _check_print_files_have_all_the_expected_data(context, expected_csv_lines, fulfilment_code)
    _check_manifest_files_created(context, fulfilment_code)


@then('correctly formatted on request supplementary material print'
      ' and manifest files for "{fulfilment_code}" are created')
def correct_supplementary_material_print_files(context, fulfilment_code):
    expected_csv_lines = create_expected_supplementary_materials_csv(context, fulfilment_code)
    _check_print_files_have_all_the_expected_data(context, expected_csv_lines, fulfilment_code)
    _check_manifest_files_created(context, fulfilment_code)


def _check_print_files_have_all_the_expected_data(context, expected_csv_lines, pack_code):
    with SftpUtility() as sftp_utility:
        _validate_print_file_content(sftp_utility, context.test_start_local_datetime, expected_csv_lines, pack_code)


@retry(retry_on_exception=lambda e: isinstance(e, FileNotFoundError), wait_fixed=1000, stop_max_attempt_number=120)
def _validate_print_file_content(sftp_utility, start_of_test, expected_csv_lines, pack_code):
    logger.debug('Checking for files on SFTP server')

    files = sftp_utility.get_all_files_after_time(start_of_test, pack_code, ".csv.gpg")

    actual_content_list = sftp_utility.get_files_content_as_list(files, pack_code)
    if not actual_content_list:
        raise FileNotFoundError
    actual_content_list.sort()
    expected_csv_lines.sort()
    test_helper.assertEquals(actual_content_list, expected_csv_lines, 'Print file contents did not match expected')


def _check_manifest_files_created(context, pack_code):
    with SftpUtility() as sftp_utility:
        files = sftp_utility.get_all_files_after_time(context.test_start_local_datetime, pack_code)

        for _file in files:
            if _file.filename.endswith(".csv.gpg"):
                csv_file = _file
                manifest_file = _get_matching_manifest_file(csv_file.filename, files)

                if manifest_file is None:
                    assert False, f'Failed to find manifest file for {csv_file.filename}'

                actual_manifest = _get_actual_manifest(sftp_utility, manifest_file, pack_code)
                creation_datetime = actual_manifest['manifestCreated']
                expected_manifest = _create_expected_manifest(sftp_utility, csv_file, creation_datetime, pack_code)
                test_helper.assertDictEqual(actual_manifest, expected_manifest)


def _get_actual_manifest(sftp_utility, manifest_file, pack_code):
    actual_manifest_json = sftp_utility.get_file_contents_as_string(f'{PACK_CODE_TO_SFTP_DIRECTORY[pack_code]}/'
                                                                    f'{manifest_file.filename}')
    return json.loads(actual_manifest_json)


def _get_matching_manifest_file(filename, files):
    manifest_filename = filename.replace(".csv.gpg", ".manifest")

    for _file in files:
        if _file.filename == manifest_filename:
            return _file

    return None


def _create_expected_manifest(sftp_utility, csv_file, created_datetime, pack_code):
    actual_file_contents = sftp_utility.get_file_contents_as_string(f'{PACK_CODE_TO_SFTP_DIRECTORY[pack_code]}'
                                                                    f'/{csv_file.filename}')

    md5_hash = hashlib.md5(actual_file_contents.encode('utf-8')).hexdigest()
    expected_size = sftp_utility.get_file_size(f'{PACK_CODE_TO_SFTP_DIRECTORY[pack_code]}/{csv_file.filename}')

    _file = dict(
        sizeBytes=str(expected_size),
        md5Sum=md5_hash,
        relativePath='./',
        name=csv_file.filename
    )

    manifest = dict(
        schemaVersion='1',
        files=[_file],
        sourceName="ONS_RM",
        manifestCreated=created_datetime,
        description=PACK_CODE_TO_DESCRIPTION[pack_code],
        dataset=PACK_CODE_TO_DATASET[pack_code],
        version='1'
    )

    return manifest
