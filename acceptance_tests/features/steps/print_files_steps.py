import json
from datetime import datetime

import paramiko
import requests
from behave import *
from retrying import retry

from config import Config
from controllers.case_controller import get_cases_by_sample_unit_ids
from exceptions import DataNotYetThereError

use_step_matcher("re")


def get_iacs_for_collection_exercise(context):
    sample_units = [
        json.loads(sample_unit).get('id')
        for sample_unit in context.sample_units.values()
    ]

    cases = get_cases_by_sample_unit_ids(sample_units)
    expected_iacs = []

    for case in cases:
        iac = get_iac_for_case_id(case["id"])
        expected_iacs.append(iac)

    return expected_iacs


@retry(retry_on_exception=lambda e: isinstance(e, DataNotYetThereError),
       wait_fixed=5000, stop_max_attempt_number=24)
def get_iac_for_case_id(case_id):
    url = f'{Config.CASE_SERVICE}/cases/{case_id}/iac'
    response = requests.get(url, auth=Config.BASIC_AUTH)
    response.raise_for_status()

    iac_list = json.loads(response.text)
    if len(iac_list) == 0:
        raise DataNotYetThereError

    iac = iac_list[0]["iac"]
    return iac


@step("the a correctly formatted file is created on the sftp server")
def step_impl(context):
    sftp_client = _get_sftp_client()
    expected_iacs = get_iacs_for_collection_exercise(context)
    _check_notification_files_have_iacs(sftp_client,
                                        context.test_start_datetime,
                                        context.survey_ref,
                                        context.period,
                                        expected_iacs)
    pass


def _get_sftp_client():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=Config.SFTP_HOST,
                port=int(Config.SFTP_PORT),
                username=Config.SFTP_USERNAME,
                password=Config.SFTP_PASSWORD,
                look_for_keys=False,
                timeout=120)
    return ssh.open_sftp()


@retry(retry_on_exception=lambda e: isinstance(e, FileNotFoundError),
       wait_fixed=5000, stop_max_attempt_number=24)
def _check_notification_files_have_iacs(client, start_of_test, survey_ref, period, expected_iacs):
    # logger.debug('Checking for files on SFTP server')
    files = _get_files_filtered_by_name_and_modified_time(client, survey_ref, period, start_of_test)
    if len(files) == 0:
        raise FileNotFoundError

    seen_iacs = []

    for file in files:
        file_path = f'{Config.SFTP_DIR}/{file.filename}'

        with client.open(file_path) as sftp_file:
            content = str(sftp_file.read())

            for iac in expected_iacs:
                if iac in content:
                    seen_iacs.append(iac)

    if set(seen_iacs) != set(expected_iacs):
        file_names = [f.filename for f in files]
        # logger.info('Unable to find all iacs', files_found=file_names, seen_iacs=seen_iacs, expected_iacs=expected_iacs)
        raise FileNotFoundError

    return True


def _get_files_filtered_by_name_and_modified_time(client, survey_ref, period, start_of_test):
    files = client.listdir_attr(Config.SFTP_DIR)
    start_of_test = _round_to_minute(start_of_test)
    files = list(filter(lambda f: f'{survey_ref}_{period}' in f.filename
                                  and start_of_test <= datetime.fromtimestamp(f.st_mtime), files))
    return files


def _round_to_minute(start_of_test):
    return datetime(start_of_test.year, start_of_test.month,
                    start_of_test.day, start_of_test.hour,
                    start_of_test.minute, second=0, microsecond=0)
