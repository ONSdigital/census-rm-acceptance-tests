import json
import logging

import requests
from retrying import retry
from structlog import wrap_logger

from config import Config
from exceptions import DataNotYetThereError

logger = wrap_logger(logging.getLogger(__name__))


@retry(retry_on_exception=lambda e: isinstance(e, DataNotYetThereError), wait_fixed=5000, stop_max_attempt_number=30)
def get_cases_by_sample_unit_ids(sample_unit_ids):
    logger.info('Retrieving cases by sample_unit_ids')

    url = f'{Config.CASE_SERVICE}/cases/sampleunitids'
    payload = {'sampleUnitId': sample_unit_ids}

    response = requests.get(url, params=payload, auth=Config.BASIC_AUTH)
    response.raise_for_status()

    cases = response.json()
    if len(cases) < len(sample_unit_ids):
        raise DataNotYetThereError

    logger.info('Successfully retrieved cases by sample_unit_ids')

    return cases


@retry(retry_on_exception=lambda e: isinstance(e, DataNotYetThereError),
       wait_fixed=5000, stop_max_attempt_number=24)
def get_1st_iac_for_case_id(case_id):
    url = f'{Config.CASE_SERVICE}/cases/{case_id}/iac'
    response = requests.get(url, auth=Config.BASIC_AUTH)
    response.raise_for_status()

    iac_list = json.loads(response.text)
    if len(iac_list) == 0:
        raise DataNotYetThereError

    return iac_list[0]["iac"]


@retry(retry_on_exception=lambda e: isinstance(e, DataNotYetThereError), wait_fixed=5000, stop_max_attempt_number=30)
def get_cases_by_survey_id(survey_id):
    logger.info('Retrieving cases by survey id')

    url = f'{Config.CASE_SERVICE}/cases/surveyid/{survey_id}'

    response = requests.get(url, auth=Config.BASIC_AUTH)
    response.raise_for_status()

    return response.json()
