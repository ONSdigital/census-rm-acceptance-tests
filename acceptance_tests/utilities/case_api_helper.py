import json
import requests

from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


def get_case_and_case_events_by_case_id(case_id):
    response = requests.get(f'{Config.CASE_API_CASE_URL}{case_id}?caseEvents=true')
    response.raise_for_status()
    return response.json()


def get_logged_events_for_case_by_id(case_id):
    response = requests.get(f'{Config.CASE_API_CASE_URL}{case_id}?caseEvents=true').content.decode("utf-8")
    response_json = json.loads(response)
    return response_json['caseEvents']


def get_ccs_qid_for_case_id(case_id):
    response = requests.get(f'{Config.CASE_API_CASE_URL}ccs/{case_id}/qid')
    test_helper.assertEqual(response.status_code, 200, 'CCS QID API call failed')
    response_json = response.json()
    return response_json
