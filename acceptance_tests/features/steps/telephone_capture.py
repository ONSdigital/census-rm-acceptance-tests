import requests
from behave import step

from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

case_api_url = f'{Config.CASEAPI_SERVICE}/cases/'


@step("there is a request for telephone capture for an english respondent with case type HH")
def request_telephone_capture_qid_uac(context):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    response = requests.get(f"{case_api_url}{context.first_case['id']}/qid")
    test_helper.assertEqual(response.status_code, 200)

    context.telephone_capture_qid_uac = response.json()


@step("generate and return a UAC and the correct english HH QID type")
def check_telephone_capture_uac_and_qid_type(context):
    test_helper.assertIsNotNone(context.telephone_capture_qid_uac.get('uac'))
    test_helper.assertEqual(context.telephone_capture_qid_uac['questionnaireId'][:2], '01')
