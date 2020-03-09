import json
import logging

import requests
from behave import then, step
import luhn
from structlog import wrap_logger

from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

logger = wrap_logger(logging.getLogger(__name__))
case_api_url = f'{Config.CASEAPI_SERVICE}/cases/'


@then("a case can be retrieved from the case API service")
def get_case_by_id(context):
    case_id = context.case_created_events[0]['payload']['collectionCase']['id']
    response = requests.get(f'{case_api_url}{case_id}')
    test_helper.assertEqual(response.status_code, 200, 'Case not found')
    context.case_details = response.json()


@then('case API returns multiple cases for a UPRN')
def find_multiple_cases_by_uprn(context):
    response = requests.get(f'{case_api_url}uprn/10008677190')
    response.raise_for_status()

    response_data = json.loads(response.content)

    test_helper.assertGreater(len(response_data), 1, 'Multiple cases not found')
    # Check some of the fields aren't blank
    for case in response_data:
        test_helper.assertTrue(case['id'], 'caseId missing')
        test_helper.assertTrue(case['caseRef'], 'caseRef missing')
        test_helper.assertTrue(case['postcode'], 'postcode missing')


@then('a case can be retrieved by its caseRef')
def find_case_by_case_ref(context):
    case_ref = context.case_created_events[0]['payload']['collectionCase']['caseRef']

    response = requests.get(f'{case_api_url}ref/{case_ref}')

    test_helper.assertEqual(response.status_code, 200, 'Case ref not found')


@step('the case API returns the CCS QID for the new case')
def validate_ccs_qid_for_case_id(context):
    response_json = get_ccs_qid_for_case_id(context.ccs_case['id'])
    test_helper.assertEqual(response_json['questionnaireId'][0:3],
                            '712', 'CCS QID has incorrect questionnaire type or tranche ID')
    test_helper.assertTrue(response_json['active'])
    test_helper.assertEqual(response_json['formType'], "H",
                            f'Expected FormType is "H" but got "{response_json["formType"]}"')


def get_ccs_qid_for_case_id(case_id):
    response = requests.get(f'{case_api_url}ccs/{case_id}/qid')
    test_helper.assertEqual(response.status_code, 200, 'CCS QID API call failed')
    response_json = response.json()
    return response_json


@step('the case API returns the new CCS case by postcode search')
def get_ccs_case_by_postcode(context):
    response = requests.get(f'{case_api_url}ccs/postcode/{context.ccs_case["postcode"]}')
    response.raise_for_status()
    found_cases = response.json()

    for case in found_cases:
        if case['id'] == context.ccs_case['id']:
            matched_case = case
            break
    else:
        test_helper.fail('Failed to find the new CCS case by postcode search')

    test_helper.assertEqual(context.ccs_case['postcode'], matched_case['postcode'])
    test_helper.assertEqual(context.ccs_case['caseRef'], matched_case['caseRef'])


@step('it contains the correct fields for a CENSUS case')
def check_census_case_fields(context):
    test_helper.assertTrue(context.case_details['caseRef'])
    test_helper.assertEquals(len(context.case_details['caseRef']), 10)
    test_helper.assertTrue(luhn.verify(context.case_details['caseRef']))

    test_helper.assertTrue(context.case_details['arid'])
    test_helper.assertTrue(context.case_details['estabArid'])
    test_helper.assertTrue(context.case_details['estabType'])
    test_helper.assertTrue(context.case_details['uprn'])
    test_helper.assertTrue(context.case_details['collectionExerciseId'])
    test_helper.assertTrue(context.case_details['createdDateTime'])
    test_helper.assertTrue(context.case_details['lastUpdated'])
    test_helper.assertTrue(context.case_details['addressLine1'])
    test_helper.assertTrue(context.case_details['addressLine2'])
    test_helper.assertTrue(context.case_details['addressLine3'])
    test_helper.assertTrue(context.case_details['townName'])
    test_helper.assertTrue(context.case_details['postcode'])
    test_helper.assertTrue(context.case_details['addressLevel'])
    test_helper.assertTrue(context.case_details['abpCode'])
    test_helper.assertTrue(context.case_details['region'])
    test_helper.assertTrue(context.case_details['latitude'])
    test_helper.assertTrue(context.case_details['longitude'])
    test_helper.assertTrue(context.case_details['oa'])
    test_helper.assertTrue(context.case_details['lsoa'])
    test_helper.assertTrue(context.case_details['msoa'])
    test_helper.assertTrue(context.case_details['lad'])
    test_helper.assertTrue(context.case_details['id'])
    test_helper.assertTrue(context.case_details['addressType'])
    test_helper.assertEqual(context.case_details['surveyType'], "CENSUS")
    test_helper.assertFalse(context.case_details['handDelivery'])


@step('it contains the correct fields for a CCS case')
def check_ccs_case_fields(context):
    test_helper.assertTrue(context.ccs_case['caseRef'])
    test_helper.assertFalse(context.ccs_case['arid'])
    test_helper.assertFalse(context.ccs_case['estabArid'])
    test_helper.assertTrue(context.ccs_case['estabType'])
    test_helper.assertFalse(context.ccs_case['uprn'])
    test_helper.assertTrue(context.ccs_case['collectionExerciseId'])
    test_helper.assertEqual(context.ccs_case['surveyType'], "CCS")
    test_helper.assertTrue(context.ccs_case['createdDateTime'])
    test_helper.assertTrue(context.ccs_case['lastUpdated'])
    test_helper.assertTrue(context.ccs_case['addressLine1'])
    test_helper.assertTrue(context.ccs_case['addressLine2'])
    test_helper.assertTrue(context.ccs_case['addressLine3'])
    test_helper.assertTrue(context.ccs_case['townName'])
    test_helper.assertTrue(context.ccs_case['postcode'])
    test_helper.assertTrue(context.ccs_case['addressLevel'])
    test_helper.assertFalse(context.ccs_case['abpCode'])
    test_helper.assertFalse(context.ccs_case['region'])
    test_helper.assertTrue(context.ccs_case['latitude'])
    test_helper.assertTrue(context.ccs_case['longitude'])
    test_helper.assertFalse(context.ccs_case['oa'])
    test_helper.assertFalse(context.ccs_case['lsoa'])
    test_helper.assertFalse(context.ccs_case['msoa'])
    test_helper.assertFalse(context.ccs_case['lad'])
    test_helper.assertTrue(context.ccs_case['id'])
    test_helper.assertTrue(context.ccs_case['addressType'])
    test_helper.assertFalse(context.ccs_case['handDelivery'])


def get_logged_events_for_case_by_id(case_id):
    response = requests.get(f'{case_api_url}{case_id}?caseEvents=true').content.decode("utf-8")
    response_json = json.loads(response)
    return response_json['caseEvents']
