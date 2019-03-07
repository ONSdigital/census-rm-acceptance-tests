import logging

from behave import *
from retrying import retry
from structlog import wrap_logger

from controllers.case_controller import get_cases_by_sample_unit_ids
from helpers.expected_print_file_data_helper import create_expected_csv_lines
from utilities.sftp_utility import SFTPUtility

logger = wrap_logger(logging.getLogger(__name__))


@Then("correctly formatted notification files are created")
def check_correct_files_on_sftp_server(context):
    expected_csv_lines = create_expected_csv_lines(context)
    _check_notification_files_have_all_the_expected_data(context, expected_csv_lines)


def _check_notification_files_have_all_the_expected_data(context, expected_csv_lines):
    with SFTPUtility() as sftp_utility:
        abc(sftp_utility, context.survey_ref, context.period, context.test_start_datetime, expected_csv_lines)


@retry(retry_on_exception=lambda e: isinstance(e, FileNotFoundError),
       wait_fixed=5000, stop_max_attempt_number=24)
def abc(sftp_utility, survey_ref, period, start_of_test, expected_csv_lines):
    logger.debug('Checking for files on SFTP server')

    files = sftp_utility.get_files_filtered_by_survey_ref_period_and_modified_date(survey_ref, period,
                                                                                   start_of_test)
    if len(files) == 0:
        raise FileNotFoundError

    actual_content_list = sftp_utility.get_files_content_as_list(files)

    if set(actual_content_list) != set(expected_csv_lines):
        file_names = [f.filename for f in files]
        logger.info('Unable to find all iacs', files_found=file_names, expected_csv_lines=expected_csv_lines,
                    actual_content_list=actual_content_list)
        raise FileNotFoundError

    return True
