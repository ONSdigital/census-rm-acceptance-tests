import hashlib
import json
import logging

from behave import then, step
from google.cloud import storage
from retrying import retry
from structlog import wrap_logger

from acceptance_tests.utilities.mappings import PACK_CODE_TO_SFTP_DIRECTORY, PACK_CODE_TO_DATASET, \
    PACK_CODE_TO_DESCRIPTION
from acceptance_tests.utilities.print_file_helper import \
    create_expected_csv_lines, create_expected_on_request_questionnaire_csv, \
    create_expected_supplementary_materials_csv, create_expected_reminder_letter_csv_lines, \
    create_expected_reminder_questionnaire_csv_lines, create_expected_on_request_fulfilment_questionnaire_csv, \
    create_expected_csv_lines_for_ce_estab_responses, create_expected_CE_Estab_questionnaire_csv_lines, \
    create_expected_questionnaire_csv_lines, create_expected_Welsh_CE_Estab_questionnaire_csv_line_endings
from acceptance_tests.utilities.sftp_utility import SftpUtility
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

logger = wrap_logger(logging.getLogger(__name__))


@then('correctly formatted "{pack_code}" print files are created for questionnaire')
def check_correct_questionnaire_files_on_sftp_server(context, pack_code):
    expected_csv_lines = create_expected_questionnaire_csv_lines(context, pack_code)
    _check_print_files_have_all_the_expected_data(context, expected_csv_lines, pack_code)


@then('correctly formatted "{pack_code}" print files are created for CE Estab questionnaires')
def check_correct_CE_Estab_questionnaire_files_on_sftp_server(context, pack_code):
    expected_csv_lines = create_expected_CE_Estab_questionnaire_csv_lines(context, pack_code)
    _check_print_files_have_all_the_expected_data(context, expected_csv_lines, pack_code)


@then('correctly formatted "{pack_code}" print files are created for CE Estab Welsh questionnaires')
def check_correct_Welsh_CE_Estab_questionnaire_files_on_sftp_server(context, pack_code):
    # in the print file, there will be multiple rows with English/Welsh UAC/QID pairs for each case
    # we do not know which English UAC/QID pair will be on which row as the Welsh UAC/QID pair is on
    # so 'line_ending' matches the case details after UAC/QID values have been assigned
    # we filter print file by 'line_ending' to get a list of rows for that case
    # then we check that Ind English and Ind Welsh UAC/QID pairs are accounted for in the filtered rows

    expected_case_data = create_expected_Welsh_CE_Estab_questionnaire_csv_line_endings(context, pack_code)

    expected_print_file_line_count = 0
    for case_id, value in expected_case_data.items():
        expected_print_file_line_count += value['case_details']['ceExpectedCapacity']

    actual_print_file_rows = check_ce_estab_welsh_questionnaire_is_correct(context, pack_code,
                                                                           expected_print_file_line_count)

    for case_id, value in expected_case_data.items():
        matching_rows = []
        for row in actual_print_file_rows:
            if row.endswith(value['line_ending']):
                matching_rows.append(row)

        test_helper.assertEqual(len(matching_rows), value['case_details']['ceExpectedCapacity'])

        for uac in context.uac_created_events:
            if uac['payload']['uac']['caseId'] == value['case_details']['id']:
                _check_uac_qid_pair_located_in_welsh_ce_estab_cases(matching_rows, uac, value)


def _check_uac_qid_pair_located_in_welsh_ce_estab_cases(matching_rows, uac, value):
    # checks ind qid type for CE Estab Welsh in Welsh case and then tests against passed rows

    if uac['payload']['uac']['questionnaireId'][:2] == '23':
        expected_welsh_line_ending = f"|{uac['payload']['uac']['uac']}|" \
                                     f"{uac['payload']['uac']['questionnaireId']}|{value['line_ending']}"
        matched = False
        for row in matching_rows:
            if row.endswith(expected_welsh_line_ending):
                matched = True

        test_helper.assertTrue(matched,
                               f'Could not find expected Welsh line ending {expected_welsh_line_ending}')

    else:
        expected_english_line_start = f"{uac['payload']['uac']['uac']}|" \
                                      f"{uac['payload']['uac']['questionnaireId']}|"
        matched = False
        for row in matching_rows:
            if row.startswith(expected_english_line_start):
                matched = True

        test_helper.assertTrue(matched,
                               f'Could not find expected English line starting '
                               f'{expected_english_line_start}')


@retry(retry_on_exception=lambda e: isinstance(e, FileNotFoundError), wait_fixed=1000, stop_max_attempt_number=120)
def check_ce_estab_welsh_questionnaire_is_correct(context, pack_code, expected_print_file_line_count):
    actual_print_file_rows = _get_print_file_rows_as_list(context, pack_code)

    if len(actual_print_file_rows) != expected_print_file_line_count:
        raise FileNotFoundError
    return actual_print_file_rows


@then('correctly formatted "{pack_code}" print files are created')
def check_correct_files_on_sftp_server(context, pack_code):
    context.expected_pack_code = pack_code
    expected_csv_lines = create_expected_csv_lines(context, pack_code)
    _check_print_files_have_all_the_expected_data(context, expected_csv_lines, pack_code)


@then('correctly formatted "{pack_code}" print files are created for CE Estab expected responses')
def check_correct_ce_estab_files_on_sftp_server(context, pack_code):
    context.expected_pack_code = pack_code
    expected_csv_lines = create_expected_csv_lines_for_ce_estab_responses(context, pack_code)
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
    expected_csv_lines = create_expected_csv_lines(context, pack_code, context.first_case['id'])
    _check_print_files_have_all_the_expected_data(context, expected_csv_lines, pack_code)


@step('skeleton cases do not appear in "{pack_code}" print files')
def check_skeleton_case_not_in_print_file(context, pack_code):
    with SftpUtility() as sftp_utility:
        _check_print_file_does_not_contain_case_ref(context, context.test_start_local_datetime, sftp_utility, pack_code)


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


@step(
    'correctly formatted on request fulfilment questionnaire '
    'print and manifest files for "{fulfilment_code}" are created')
def correct_on_request_fulfilment_questionnaire_print_files(context, fulfilment_code):
    expected_csv_lines = create_expected_on_request_fulfilment_questionnaire_csv(context, fulfilment_code)
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
        _validate_print_file_content(context, sftp_utility, context.test_start_local_datetime, expected_csv_lines,
                                     pack_code)


def _get_print_file_rows_as_list(context, pack_code):
    with SftpUtility() as sftp_utility:
        context.expected_print_files = sftp_utility.get_all_files_after_time(context.test_start_local_datetime,
                                                                             pack_code, ".csv.gpg")
        return sftp_utility.get_files_content_as_list(context.expected_print_files, pack_code)


@retry(retry_on_exception=lambda e: isinstance(e, FileNotFoundError), wait_fixed=1000, stop_max_attempt_number=120)
def _validate_print_file_content(context, sftp_utility, start_of_test, expected_csv_lines, pack_code):
    logger.debug('Checking for files on SFTP server')

    context.expected_print_files = sftp_utility.get_all_files_after_time(start_of_test, pack_code, ".csv.gpg")

    actual_content_list = sftp_utility.get_files_content_as_list(context.expected_print_files, pack_code)
    if not actual_content_list:
        raise FileNotFoundError
    actual_content_list.sort()
    expected_csv_lines.sort()
    test_helper.assertEquals(actual_content_list, expected_csv_lines, 'Print file contents did not match expected')


@retry(retry_on_exception=lambda e: isinstance(e, FileNotFoundError), wait_fixed=1000, stop_max_attempt_number=120)
def _check_print_file_does_not_contain_case_ref(context, start_of_test, sftp_utility, pack_code):
    logger.debug('Checking for files on SFTP server')
    context.expected_print_files = sftp_utility.get_all_files_after_time(start_of_test, pack_code, ".csv.gpg")
    actual_content_list = sftp_utility.get_files_content_as_list(context.expected_print_files, pack_code)
    if not actual_content_list:
        raise FileNotFoundError
    test_helper.assertFalse(any(
        context.case_created_events[0]['payload']['collectionCase']['caseRef'] in row for row in actual_content_list))


def _check_manifest_files_created(context, pack_code):
    with SftpUtility() as sftp_utility:
        files = sftp_utility.get_all_files_after_time(context.test_start_local_datetime, pack_code)

        for _file in files:
            if _file.filename.endswith(".csv.gpg"):
                csv_file = _file
                manifest_file = _get_matching_manifest_file(csv_file.filename, files)

                if manifest_file is None:
                    test_helper.fail(f'Failed to find manifest file for {csv_file.filename}')

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
    decrypted_file_contents = sftp_utility.decrypt_message(actual_file_contents)

    md5_hash = hashlib.md5(actual_file_contents.encode('utf-8')).hexdigest()
    expected_size = sftp_utility.get_file_size(f'{PACK_CODE_TO_SFTP_DIRECTORY[pack_code]}/{csv_file.filename}')

    _file = dict(
        sizeBytes=str(expected_size),
        md5sum=md5_hash,
        relativePath='./',
        name=csv_file.filename,
        rows=len(decrypted_file_contents.splitlines())
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


@step("the files have all been copied to the bucket")
def check_files_are_copied_to_gcp_bucket(context):
    if len(Config.SENT_PRINT_FILE_BUCKET) == 0:
        logger.info('Ignoring GCP bucket check as bucket name not set')
        return

    client = storage.Client()
    bucket = client.get_bucket(Config.SENT_PRINT_FILE_BUCKET)

    for print_file in context.expected_print_files:
        compare_sftp_with_gcp_files(context, bucket, print_file.filename)
        compare_sftp_with_gcp_files(context, bucket, print_file.filename.replace(".csv.gpg", ".manifest"))


def compare_sftp_with_gcp_files(context, bucket, filename):
    blob = bucket.get_blob(filename)
    actual_file_content = blob.download_as_string().decode("utf-8")

    with SftpUtility() as sftp_utility:
        file_path = f'{PACK_CODE_TO_SFTP_DIRECTORY[context.expected_pack_code]}/{filename}'
        expected_file_content = sftp_utility.get_file_contents_as_string(file_path)

    test_helper.assertEquals(actual_file_content, expected_file_content,
                             f'file contents {filename} did not match gcp file contents')
