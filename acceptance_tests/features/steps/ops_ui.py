import operator

import requests
from behave import step, then
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
    sorted_cases = sorted(context.cases_by_postcode,
                          key=operator.itemgetter('organisationName', 'addressLine1', 'caseType', 'addressLevel'))

    # Check the order returned by case API
    unittest_helper.assertEqual(context.cases_by_postcode, sorted_cases,
                                'The API should return the cases in the correct order')

    # Check the expected data is on the page
    postcode_result_text = context.postcode_result.text
    unittest_helper.assertIn(f'{context.number_of_cases} results for postcode: "{context.postcode}"',
                             postcode_result_text)
    case_page_locations = []
    for case in context.cases_by_postcode:
        unittest_helper.assertIn(case['caseRef'], postcode_result_text)
        unittest_helper.assertIn(case['addressLine1'], postcode_result_text)
        unittest_helper.assertIn(case['uprn'], postcode_result_text)
        unittest_helper.assertIn(case['estabType'], postcode_result_text)
        case_page_locations.append({'id': case['id'], 'location': postcode_result_text.find(case['caseRef'])})

    # Check the cases appear in the expected order on the page
    case_order_on_page = [case['id'] for case in sorted(case_page_locations, key=operator.itemgetter('location'))]
    unittest_helper.assertEqual(case_order_on_page, [case['id'] for case in sorted_cases],
                                'The order of cases should be in order on the page')


@step("the user submits a qid to be linked to the case")
def submit_qid_link_on_r_ops(context):
    unittest_helper.assertIn('Submit QID Link', context.case_details_text)
    payload = {'case_id': context.case_details['id'],
               'qid': context.requested_qid}
    context.qid_link_response = requests.post(
        f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}/case-details/questionnaire-id'
        f'/link/', data=payload)

    unittest_helper.assertEqual(context.qid_link_response.status_code, 200)


@step("the user enters a qid they would like to link to the case")
def entering_in_qid_to_see_if_it_exists(context):
    payload = {'case_id': context.case_details['id'],
               'qid': context.requested_qid}

    context.qid_link_response = requests.get(
        f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}/case-details'
        f'/questionnaire-id/', params=payload)

    unittest_helper.assertEqual(context.qid_link_response.status_code, 200)


@step("the user submits a fake qid to be linked to the case")
def submit_qid_link_on_r_ops(context):
    unittest_helper.assertIn('Submit QID Link', context.case_details_text)
    context.qid_link_response = requests.get(
        f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}/case-details'
        f'/questionnaire-id/?qid=123456789&case_id={context.case_details["id"]}')

    unittest_helper.assertEqual(context.qid_link_response.status_code, 200)



@then("a qid linked message appears on the screen")
def qid_linked_message_appears(context):
    response_text = context.qid_link_response.text

    unittest_helper.assertIn('QID link has been submitted', response_text)
    unittest_helper.assertIn('QUESTIONNAIRE_LINKED', response_text)
    unittest_helper.assertIn(f'{context.requested_qid}', response_text)


@then("a failed to find qid message appears on r ops ui")
def qid_failed_message(context):
    response_text = context.qid_link_response.text

    unittest_helper.assertIn('QID does not exist in RM', response_text)


@then("the qid details page appears")
def qid_details_page(context):
    response_text = context.qid_link_response.text

    unittest_helper.assertIn(f'<b>questionnaireId:</b> {context.requested_qid}', response_text)
