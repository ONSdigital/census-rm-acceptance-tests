import json
import logging
from random import randint
from uuid import uuid4

import requests
from behave import then, given, step
from structlog import wrap_logger

from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

logger = wrap_logger(logging.getLogger(__name__))
case_api_url = f'{Config.CASEAPI_SERVICE}/cases/'


@then("a case can be retrieved from the case API service")
def get_case_by_id(context):
    case_id = context.case_created_events[0]['payload']['collectionCase']['id']

    response = requests.get(f'{case_api_url}{case_id}')

    context.response = response.json()

    test_helper.assertEqual(response.status_code, 200, 'Case not found')


@given('a random caseId is generated')
def generate_random_uuid(context):
    dummy_case_id = uuid4()
    context.test_endpoint_with_non_existent_value = dummy_case_id
    logger.info(f'Dummy caseId = {dummy_case_id}')


@given('a random uprn is generated')
def generate_random_uprn(context):
    random_uprn = randint(15000000000, 19999999999)
    context.test_endpoint_with_non_existent_value = f'uprn/{random_uprn}'
    logger.info(f'Dummy uprn = {random_uprn}')


@given('a random caseRef is generated')
def generate_random_case_ref(context):
    random_case_ref = randint(15000000, 19999999)
    context.test_endpoint_with_non_existent_value = f'ref/{random_case_ref}'
    logger.info(f'Dummy caseRef = {random_case_ref}')


@then('case API should return a 404 when queried')
def get_non_existent_case_id(context):
    response = requests.get(f'{case_api_url}{context.test_endpoint_with_non_existent_value}')

    test_helper.assertEqual(response.status_code, 404, 'A case was returned when none were expected')


@then('case API returns multiple cases for a UPRN')
def find_multiple_cases_by_uprn(context):
    response = requests.get(f'{case_api_url}uprn/10008677190')
    response.raise_for_status()

    response_data = json.loads(response.content)

    assert len(response_data) > 1, 'Multiple cases not found'
    # Check some of the fields aren't blank
    for case in response_data:
        assert case['id'], 'caseId missing'
        assert case['caseRef'], 'caseRef missing'
        assert case['postcode'], 'postcode missing'


@then('a case can be retrieved by its caseRef')
def find_case_by_case_ref(context):
    case_ref = context.case_created_events[0]['payload']['collectionCase']['caseRef']

    response = requests.get(f'{case_api_url}ref/{case_ref}')

    test_helper.assertEqual(response.status_code, 200, 'Case ref not found')


@step('the case API returns the CCS QID for the new case')
def get_ccs_qid_for_case_id(context):
    response = requests.get(f'{case_api_url}ccs/{context.ccs_case["id"]}/qid')
    test_helper.assertEqual(response.status_code, 200, 'CCS QID API call failed')
    response_json = json.loads(response.text)
    test_helper.assertEqual(response_json['qid'][0:3], '712', 'CCS QID has incorrect questionnaire type or tranche ID')
    test_helper.assertTrue(response_json['active'])


@step('it contains the correct fields for a CENSUS case')
def check_census_case_fields(context):
    assert context.response['caseRef']
    assert context.response['arid']
    assert context.response['estabArid']
    assert context.response['estabType']
    assert context.response['uprn']
    assert context.response['collectionExerciseId']
    test_helper.assertEqual(context.response['surveyType'], "CENSUS")
    assert context.response['createdDateTime']
    assert context.response['addressLine1']
    assert context.response['addressLine2']
    assert context.response['addressLine3']
    assert context.response['townName']
    assert context.response['postcode']
    assert context.response['addressLevel']
    assert context.response['abpCode']
    assert context.response['region']
    assert context.response['latitude']
    assert context.response['longitude']
    assert context.response['oa']
    assert context.response['lsoa']
    assert context.response['msoa']
    assert context.response['lad']
    assert context.response['state']
    assert context.response['id']
    assert context.response['caseType']


@step('it contains the correct fields for a CCS case')
def check_ccs_case_fields(context):
    assert context.ccs_case['caseRef']
    test_helper.assertFalse(context.ccs_case['arid'])
    test_helper.assertFalse(context.ccs_case['estabArid'])
    assert context.ccs_case['estabType']
    test_helper.assertFalse(context.ccs_case['uprn'])
    assert context.ccs_case['collectionExerciseId']
    test_helper.assertEqual(context.ccs_case['surveyType'], "CCS")
    assert context.ccs_case['createdDateTime']
    assert context.ccs_case['addressLine1']
    assert context.ccs_case['addressLine2']
    assert context.ccs_case['addressLine3']
    assert context.ccs_case['townName']
    assert context.ccs_case['postcode']
    assert context.ccs_case['addressLevel']
    test_helper.assertFalse(context.ccs_case['abpCode'])
    test_helper.assertFalse(context.ccs_case['region'])
    assert context.ccs_case['latitude']
    assert context.ccs_case['longitude']
    test_helper.assertFalse(context.ccs_case['oa'])
    test_helper.assertFalse(context.ccs_case['lsoa'])
    test_helper.assertFalse(context.ccs_case['msoa'])
    test_helper.assertFalse(context.ccs_case['lad'])
    assert context.ccs_case['state']
    assert context.ccs_case['id']
    assert context.ccs_case['caseType']


def get_logged_events_for_case_by_id(case_id):
    response = requests.get(f'{case_api_url}{case_id}?caseEvents=true').content.decode("utf-8")
    response_json = json.loads(response)
    return response_json['caseEvents']
