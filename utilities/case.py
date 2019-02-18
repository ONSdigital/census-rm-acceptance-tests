import requests
from retrying import retry

from config import Config
from utilities.Exceptions import DataNotYetThereError


@retry(retry_on_exception=lambda e: isinstance(e, DataNotYetThereError), wait_fixed=5000, stop_max_attempt_number=30)
def get_cases(sample_units):
    cases_response = get_all_cases_from_casesvc(sample_units)

    cases_response.raise_for_status()
    case_count = len(cases_response.json())

    if case_count < sample_units:
        raise DataNotYetThereError

    return cases_response


def get_all_cases_from_casesvc(sample_units):
    sample_unit_ids=list(sample_units.values())

    x = []
    d = {}
    for b in sample_unit_ids:
        i = b.split(': ')
        d[i[0]] = i[1]
        x.append(d['id'])

    # sample_unit_ids = [sample_unit['id'] for sample_unit in sample_units]
    casesvc_url = f'{Config.CASE_SERVICE}/cases'
    response = requests.get(casesvc_url, auth=Config.BASIC_AUTH)
    return response
