import operator

import requests
from behave import step
from toolbox.tests import unittest_helper

from acceptance_tests.utilities.case_api_helper import get_cases_from_postcode
from config import Config


@step("a user is on the r-ops-ui home page ready to search")
def rops_home_page(context):
    home_page_response = requests.get(f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}')
    home_page_response.raise_for_status()
    home_text = home_page_response.text
    unittest_helper.assertIn('Enter a postcode', home_text)


@step('a user navigates to the case details page for the chosen case')
def rops_get_case_details_page(context):
    context.case_details = context.case_created_events[0]['payload']['collectionCase']
    case_details_page_response = requests.get(
        f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}/case-details?case_id={context.first_case["id"]}')
    case_details_page_response.raise_for_status()
    context.case_details_text = case_details_page_response.text


@step("the user can see all case details for the chosen case")
@step("the user can see all case details for the chosen case except for the RM_UAC_CREATED event")
def rops_check_case_details_page(context):
    unittest_helper.assertIn(context.case_details["caseRef"], context.case_details_text)
    unittest_helper.assertIn(context.case_details["address"]["addressLevel"], context.case_details_text)
    unittest_helper.assertIn(context.case_details["caseType"], context.case_details_text)
    unittest_helper.assertIn(str(context.case_details["skeleton"]), context.case_details_text)
    unittest_helper.assertIn(context.case_details["collectionExerciseId"], context.case_details_text)
    unittest_helper.assertIn(context.case_details["lsoa"], context.case_details_text)
    unittest_helper.assertNotIn("RM_UAC_CREATED", context.case_details_text)


@step("a user searches for cases by postcode")
@step("a user has searched for cases")
def rops_search_postcode(context):
    context.postcode = context.case_created_events[0]['payload']['collectionCase']['address']['postcode']
    context.cases_by_postcode = get_cases_from_postcode(context.postcode)
    context.number_of_cases = len(context.cases_by_postcode)
    context.postcode_result = requests.get(
        f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}/postcode?postcode={context.postcode}')
    context.postcode_result.raise_for_status()


@step('the cases are presented to the user in order')
def rops_results(context):
    # Check the order directly from case API not the UI page for now until UI is more testable
    sorted_cases = sorted(context.cases_by_postcode,
                          key=operator.itemgetter('organisationName', 'addressLine1', 'caseType', 'addressLevel'))
    unittest_helper.assertEqual(sorted_cases, context.cases_by_postcode, 'The API should return the cases in the correct order')

    postcode_result_text = context.postcode_result.text
    unittest_helper.assertIn(f'{context.number_of_cases} results for postcode: "{context.postcode}"',
                             postcode_result_text)

    for case in context.cases_by_postcode:
        unittest_helper.assertIn(case['caseRef'], postcode_result_text)
        unittest_helper.assertIn(case['addressLine1'], postcode_result_text)
        unittest_helper.assertIn(case['uprn'], postcode_result_text)
        unittest_helper.assertIn(case['estabType'], postcode_result_text)
