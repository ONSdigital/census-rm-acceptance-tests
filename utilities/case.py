import requests
from retrying import retry

from config import Config
from utilities.Exceptions import DataNotYetThereError


@retry(retry_on_exception=lambda e: isinstance(e, DataNotYetThereError), wait_fixed=5000, stop_max_attempt_number=30)
def get_cases(required_count):
    cases_response = get_all_cases_from_casesvc()

    cases_response.raise_for_status()
    case_count = len(cases_response.json())

    if case_count < required_count:
        raise DataNotYetThereError

    return cases_response


def get_all_cases_from_casesvc():
    casesvc_url = f'{Config.CASE_SERVICE}/cases'
    response = requests.get(casesvc_url, auth=Config.BASIC_AUTH)
    return response
