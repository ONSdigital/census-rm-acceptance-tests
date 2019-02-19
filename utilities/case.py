import requests
from retrying import retry

from config import Config
from utilities.Exceptions import DataNotYetThereError
import json

# @retry(retry_on_exception=lambda e: isinstance(e, DataNotYetThereError), wait_fixed=5000, stop_max_attempt_number=30)
# def get_cases(sample_units):
#     cases_response = get_all_cases_from_casesvc(sample_units)
#
#     cases_response.raise_for_status()
#     case_count = len(cases_response.json())
#
#     if case_count < sample_units:
#         raise DataNotYetThereError
#
#     return cases_response


@retry(retry_on_exception=lambda e: isinstance(e, DataNotYetThereError), wait_fixed=5000, stop_max_attempt_number=30)
def get_all_cases_from_casesvc(sample_units):

    url = f'{Config.CASE_SERVICE}/cases/sampleunitids'
    payload = {'sampleUnitId': sample_units}

    response = requests.get(url, params=payload, auth=Config.BASIC_AUTH)
    response.raise_for_status()

    cases = response.json()

    if len(cases) < len(sample_units):
        raise DataNotYetThereError

    return response.json()
