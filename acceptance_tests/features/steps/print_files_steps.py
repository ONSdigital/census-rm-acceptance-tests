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


@step("the a correctly formatted file is created on the sftp server")
def check_correct_files_on_sftp_server(context):
    sftp_client = _get_sftp_client()
    expected_iacs = get_iacs_for_collection_exercise(context)

    _check_notification_files_have_iacs(sftp_client,
                                        context.test_start_datetime,
                                        context.survey_ref,
                                        context.period,
                                        expected_iacs)

    check_files_have_correct_data(sftp_client, context)


def check_files_have_correct_data(sftp_client, context):
    sample_units = [
        json.loads(sample_unit)
        for sample_unit in context.sample_units.values()
    ]

    expected_data_unrefined = add_full_info_to_sample_units(sample_units, context.cases)

    expected_data = "hello world"

    expected_data = []

    # Office for National Statistics:  ADDRESS_LINE1
    # Segensworth Road:  ADDRESS_LINE2
    # PO15 5RR: POSTCODE
    # Titchfield: TOWN_NAME
    # Hampshire: LOCALITY
    # E: COUNTRY
    # 3hj7gj5vxtch: (not in attributes)  "iac"
    # OHS000001: TLA + REFERENCE
    # 15 / 03  return by date?, hard code for now, it'll break if left

    for exp in expected_data_unrefined:
        atts = exp["attributes"]
        csv_line = atts["ADDRESS_LINE1"] + ":"
        csv_line += atts["ADDRESS_LINE2"] + ":"
        csv_line += atts["POSTCODE"] + ":"
        csv_line += atts["TOWN_NAME"] + ":"
        csv_line += atts["LOCALITY"] + ":"
        csv_line += atts["COUNTRY"] + ":"
        csv_line += exp["iac"] + ":"
        csv_line += atts["TLA"] + atts["REFERENCE"] + ":"
        csv_line += "15/03"
        expected_data.append(csv_line)


    _check_notification_files_have_all_the_expected_data(sftp_client,
                                                         context.test_start_datetime,
                                                         context.survey_ref,
                                                         context.period,
                                                         expected_data)


def get_iac_for_sample_unit(sample_unit_id, cases):
    for case in cases:
        if case["sampleUnitId"] == sample_unit_id:
            return case["iac"]

    return f"iac not found in for sample unit id {sample_unit_id}"


def add_full_info_to_sample_units(sample_units, cases):
    enriched_sample_units = []

    for sample_unit in sample_units:
        iac = get_iac_for_sample_unit(sample_unit["id"], cases)
        sample_unit.update({'iac': iac})
        enriched_sample_units.append(sample_unit)

    return enriched_sample_units


def get_iacs_for_collection_exercise(context):
    sample_units = [
        json.loads(sample_unit).get('id')
        for sample_unit in context.sample_units.values()
    ]

    cases = get_cases_by_sample_unit_ids(sample_units)
    expected_iacs = []
    enriched_cases = []

    for case in cases:
        iac = get_iac_for_case_id(case["id"])
        case.update({'iac': iac})
        expected_iacs.append(iac)
        enriched_cases.append(case)

    context.cases = enriched_cases

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

    return files


@retry(retry_on_exception=lambda e: isinstance(e, FileNotFoundError),
       wait_fixed=5000, stop_max_attempt_number=24)
def _check_notification_files_have_all_the_expected_data(client, start_of_test, survey_ref, period, expected_data):
    # logger.debug('Checking for files on SFTP server')
    files = _get_files_filtered_by_name_and_modified_time(client, survey_ref, period, start_of_test)
    if len(files) == 0:
        raise FileNotFoundError

    seen_iacs = []

    total_content_lines = 0

    for file in files:
        file_path = f'{Config.SFTP_DIR}/{file.filename}'

        with client.open(file_path) as sftp_file:
            content = str(sftp_file.read())

            for iac in expected_data:
                if iac in content:
                    seen_iacs.append(iac)

            total_content_lines += content.count('\\n')

    if set(seen_iacs) != set(expected_data):
        file_names = [f.filename for f in files]
        # logger.info('Unable to find all iacs', files_found=file_names, seen_iacs=seen_iacs, expected_iacs=expected_iacs)
        raise FileNotFoundError

    if total_content_lines != len(expected_data):
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
