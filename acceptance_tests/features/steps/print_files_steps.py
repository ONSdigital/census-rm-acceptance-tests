import logging
from datetime import datetime

from behave import *
from retrying import retry
from structlog import wrap_logger

from config import Config
from controllers.case_controller import get_cases_by_sample_unit_ids, get_1st_iac_for_case_id
from utilities.sftp_utility import create_open_sftp_client

use_step_matcher("re")

logger = wrap_logger(logging.getLogger(__name__))


@step("the the correctly formatted files are created on the sftp server")
def check_correct_files_on_sftp_server(context):
    sftp_client = create_open_sftp_client()
    _get_iacs_and_apply_to_sample_units(context)
    expected_csv_lines = _create_expected_csv_lines(context)

    _check_notification_files_have_all_the_expected_data(sftp_client,
                                                         context.test_start_datetime,
                                                         context.survey_ref,
                                                         context.period,
                                                         expected_csv_lines)


def _get_iacs_and_apply_to_sample_units(context):
    cases = _get_cases_with_iacs_for_sample_units(context)
    _add_iac_to_sample_units(context.sample_units, cases)


def _create_expected_csv_lines(context):
    return [
        _create_expected_csv_line(expected_data, context.collex_return_by_date)
        for expected_data in context.sample_units
    ]


@retry(retry_on_exception=lambda e: isinstance(e, FileNotFoundError),
       wait_fixed=5000, stop_max_attempt_number=24)
def _check_notification_files_have_all_the_expected_data(sftp_client, start_of_test, survey_ref, period,
                                                         expected_csv_lines):
    logger.debug('Checking for files on SFTP server')

    files = _get_files_filtered_by_survey_ref_period_and_modified_date(sftp_client, survey_ref, period, start_of_test)
    if len(files) == 0:
        raise FileNotFoundError

    actual_content_list = _get_files_content_as_list(sftp_client, files)

    if set(actual_content_list) != set(expected_csv_lines):
        file_names = [f.filename for f in files]
        logger.info('Unable to find all iacs', files_found=file_names, expected_csv_lines=expected_csv_lines,
                    actual_content_list=actual_content_list)
        raise FileNotFoundError

    return True


def _create_expected_csv_line(expected_data, return_by_date):
    attributes = expected_data["attributes"]

    return (
        f'{attributes["ADDRESS_LINE1"]}:'
        f'{attributes["ADDRESS_LINE2"]}:'
        f'{attributes["POSTCODE"] }:'
        f'{attributes["TOWN_NAME"]}:'
        f'{attributes["LOCALITY"]}:'
        f'{attributes["COUNTRY"]}:'
        f'{expected_data["iac"]}:'
        f'{attributes["TLA"]}{ attributes["REFERENCE"]}:'
        f'{return_by_date}'
    )


def _add_iac_to_sample_units(sample_units, cases):
    for sample_unit in sample_units:
        iac = _get_iac_for_sample_unit(sample_unit["id"], cases)
        sample_unit.update({'iac': iac})


def _get_iac_for_sample_unit(sample_unit_id, cases):
    for case in cases:
        if case["sampleUnitId"] == sample_unit_id:
            return case["iac"]

    # or raise an exception here?
    return f"iac not found for sample unit id {sample_unit_id}"


def _get_cases_with_iacs_for_sample_units(context):
    sample_units = _extract_sample_unit_ids(context.sample_units)
    cases = get_cases_by_sample_unit_ids(sample_units)

    cases = [
        _get_iac_and_apply_to_case(case)
        for case in cases
    ]

    return cases


def _get_iac_and_apply_to_case(case):
    iac = get_1st_iac_for_case_id(case["id"])
    case.update({'iac': iac})
    return case


def _get_files_content_as_list(sftp_client, files):
    actual_content = []

    for file in files:
        content_list = _get_file_lines_as_list(sftp_client, file)
        actual_content.extend(content_list)

    return actual_content


def _get_file_lines_as_list(sftp_client, file):
    file_path = f'{Config.SFTP_DIR}/{file.filename}'
    with sftp_client.open(file_path) as sftp_file:
        content = sftp_file.read().decode('utf-8')
        return content.rstrip().split('\n')


def _get_files_filtered_by_survey_ref_period_and_modified_date(client, survey_ref, period, start_of_test):
    files = client.listdir_attr(Config.SFTP_DIR)
    start_of_test = _round_to_minute(start_of_test)

    return list(filter(lambda f: f'{survey_ref}_{period}' in f.filename
                                 and start_of_test <= datetime.fromtimestamp(f.st_mtime), files))


def _round_to_minute(start_of_test):
    return datetime(start_of_test.year, start_of_test.month,
                    start_of_test.day, start_of_test.hour,
                    start_of_test.minute, second=0, microsecond=0)


def _extract_sample_unit_ids(sample_units):
    return [
        sample_unit['id']
        for sample_unit in sample_units
    ]
