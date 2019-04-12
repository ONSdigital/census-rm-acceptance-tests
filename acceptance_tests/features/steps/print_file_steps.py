import datetime
import json
import logging

from behave import then
from retrying import retry
from structlog import wrap_logger

from acceptance_tests.utilities.date_utilities import convert_datetime_to_str
from acceptance_tests.utilities.print_file_helper import create_expected_csv_lines
from acceptance_tests.utilities.sftp_utility import SftpUtility

logger = wrap_logger(logging.getLogger(__name__))


@then('correctly formatted print files are created')
def check_correct_files_on_sftp_server(context):
    expected_csv_lines = create_expected_csv_lines(context)
    _check_notification_files_have_all_the_expected_data(context, expected_csv_lines)


def _check_notification_files_have_all_the_expected_data(context, expected_csv_lines):
    with SftpUtility() as sftp_utility:
        _validate_print_file_content(sftp_utility, context.survey_ref, context.period,
                                     context.test_start_datetime, expected_csv_lines)


@retry(retry_on_exception=lambda e: isinstance(e, FileNotFoundError), wait_fixed=5000, stop_max_attempt_number=24)
def _validate_print_file_content(sftp_utility, survey_ref, period, start_of_test, expected_csv_lines):
    logger.debug('Checking for files on SFTP server')

    files = sftp_utility.get_files_filtered_by_survey_ref_period_and_modified_date(survey_ref, period, start_of_test)
    actual_content_list = sftp_utility.get_files_content_as_list(files)

    if set(actual_content_list) != set(expected_csv_lines):
        file_names = [f.filename for f in files]
        logger.info('Unable to find all expected data in existing files', files_found=file_names,
                    expected_csv_lines=expected_csv_lines, actual_content_list=actual_content_list)
        raise FileNotFoundError

    return True


@then("there is a correct manifest file for each csv file written")
def step_impl(context):
    logger.debug("checking manifest files exist for csv files")
    _check_manifest_files_created(context)


def _create_expected_manifest(_file):
    hardcoded_base = dict(
        schemaVersion=1,
        sourceName="ONS_RM",
        manifestCreated=convert_datetime_to_str(datetime.utcnow()),
        description="initial contact letters",
        dataset="PPD1.1",
        version=1
    )

    return hardcoded_base


def _check_manifest_files_created(context):
    with SftpUtility() as sftp_utility:
        # get list of csv files created after start of test, this works as long as tests not run in parrallel (could have partial csv files)
        files = sftp_utility.get_files_after_datetime(context.test_start_datetime)

        for _file in files:
            if _file.filename.endswith(".csv"):
                manifest_file = _get_matching_manifest_file(_file.filename, files)

                # pythonic way? Also quite nested here...
                if manifest_file is None:
                    assert False, f'Failed to find manifest file for {_file.filename}'

                actual_manifest_json = sftp_utility._get_file_contents_as_string(_file.filename)

                actual_manifest = json.loads(actual_manifest_json)
                expected_manifest = _create_expected_manifest(_file)

                a = expected_manifest



def _get_matching_manifest_file(filename, files):

    manifest_filename = filename.replace(".csv", ".manifest")

    for _file in files:
        if _file.filename == manifest_filename:
            return _file

    return None
