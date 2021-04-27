import functools
import operator

import requests
from behave import step, then

from acceptance_tests.utilities.case_api_helper import get_cases_from_postcode
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, \
    store_all_uac_updated_msgs_by_collection_exercise_id
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step("a user is on the r-ops-ui home page ready to search")
def rops_home_page(context):
    home_page_response = requests.get(f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}')
    home_page_response.raise_for_status()
    home_text = home_page_response.text
    test_helper.assertIn('Enter a postcode', home_text)


@step('a user navigates to the case details page for the chosen case')
def rops_get_case_details_page(context):
    context.case_details = context.case_created_events[0]['payload']['collectionCase']
    context.case_details_text = get_case_details_page(context.first_case['id']).text
    test_helper.assertIn('Link QID', context.case_details_text)


@step('a user navigates to the case details page for the chosen CCS case')
def rops_get_CCS_case_details_page(context):
    context.case_details = context.first_case
    context.case_details_text = get_case_details_page(context.first_case['id']).text
    test_helper.assertIn('Link QID', context.case_details_text)


@step("the user can see all case details for the chosen case")
@step("the user can see all case details for the chosen case except for the RM_UAC_CREATED event")
def rops_check_case_details_page(context):
    test_helper.assertIn(context.case_details["caseRef"], context.case_details_text)
    test_helper.assertIn(context.case_details["address"]["addressLevel"], context.case_details_text)
    test_helper.assertIn(context.case_details["caseType"], context.case_details_text)
    test_helper.assertIn(str(context.case_details["skeleton"]), context.case_details_text)
    test_helper.assertIn(context.case_details["collectionExerciseId"], context.case_details_text)
    test_helper.assertIn(context.case_details["lsoa"], context.case_details_text)
    test_helper.assertNotIn("RM_UAC_CREATED", context.case_details_text)


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
    test_helper.assertEqual(context.cases_by_postcode, sorted_cases,
                            'The API should return the cases in the correct order')

    # Check the expected data is on the page
    postcode_result_text = context.postcode_result.text
    test_helper.assertIn(f'{context.number_of_cases} results for postcode: "{context.postcode}"',
                         postcode_result_text)
    case_page_locations = []
    for case in context.cases_by_postcode:
        test_helper.assertIn(case['caseRef'], postcode_result_text)
        test_helper.assertIn(case['addressLine1'], postcode_result_text)
        test_helper.assertIn(case['uprn'], postcode_result_text)
        test_helper.assertIn(case['estabType'], postcode_result_text)
        case_page_locations.append({'id': case['id'], 'location': postcode_result_text.find(case['caseRef'])})

    # Check the cases appear in the expected order on the page
    case_order_on_page = [case['id'] for case in sorted(case_page_locations, key=operator.itemgetter('location'))]
    test_helper.assertEqual(case_order_on_page, [case['id'] for case in sorted_cases],
                            'The order of cases should be in order on the page')


@step('the user confirms they wish to link the QID to be linked')
def submit_qid_link_on_r_ops(context):
    test_helper.assertIn('Link QID', context.case_details_text)
    context.qid_link_response = submit_rops_qid_link(case_id=context.case_details['id'], qid=context.requested_qid)
    test_helper.assertEqual(context.qid_link_response.status_code, 200)


@step('the user submits a QID to be linked to the case')
@step("the user enters a QID they would like to link to the case")
@step('the user submits the CCS QID to be linked to the case')
@step('the user submits the non CCS QID to be linked to the case')
def get_case_details_link_qid(context):
    context.qid_link_response = get_rops_qid_link_page(case_id=context.case_details['id'], qid=context.requested_qid)
    test_helper.assertEqual(context.qid_link_response.status_code, 200)


@step('the QID link confirmation page appears')
def check_qid_link_confirmation_page(context):
    qid_link_page = context.qid_link_response.text
    test_helper.assertIn('Confirm linking this QID and Case ID', qid_link_page)
    test_helper.assertIn(f'<b>QID:</b> {context.requested_qid}', qid_link_page)
    test_helper.assertIn(f'<b>Case ID:</b> {context.case_details["id"]}', qid_link_page)
    test_helper.assertIn('Link QID', qid_link_page)


@step("the user submits a bad qid to be linked to the case")
def search_for_fake_qid(context):
    test_helper.assertIn('Link QID', context.case_details_text)
    context.qid_link_response = get_rops_qid_link_page(case_id=context.case_details['id'], qid='nonsense')

    test_helper.assertEqual(context.qid_link_response.status_code, 200)


@then("a QID link submitted message is flashed")
def qid_linked_message_appears(context):
    response_text = context.qid_link_response.text

    test_helper.assertIn('QID link has been submitted', response_text)


@then("a failed to find QID message is flashed")
def qid_failed_message(context):
    response_text = context.qid_link_response.text

    test_helper.assertIn('QID does not exist in RM', response_text)


@then('an error message telling them linking a CCS QID to a non CCS case is forbidden is flashed')
def linking_ccs_qid_to_census_case_forbidden_message(context):
    response_text = context.qid_link_response.text

    test_helper.assertIn('Linking a CCS QID to a non CCS case is forbidden', response_text)


@then('an error message telling them linking a non CCS QID to a CCS case is forbidden is flashed')
def linking_non_ccs_qid_to_ccs_case_forbidden_message(context):
    response_text = context.qid_link_response.text

    test_helper.assertIn('Linking a non CCS QID to a CCS case is forbidden', response_text)


@then("the QID details page is flashed")
def qid_details_page(context):
    response_text = context.qid_link_response.text

    test_helper.assertIn(f'<b>QID:</b> {context.requested_qid}', response_text)


@step('a UAC_UPDATED message is emitted linking the submitted QID to the chosen case')
def check_uac_updated_message(context):
    check_correct_uac_updated_message_is_emitted_for_rops_link(context)


def get_rops_qid_link_page(case_id, qid):
    response = requests.get(
        f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}/case-details/link-qid/',
        params={'case_id': case_id, 'qid': qid})
    response.raise_for_status()
    return response


def submit_rops_qid_link(case_id, qid):
    response = requests.post(
        f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}/case-details/link-qid/submit/',
        data={'case_id': case_id, 'qid': qid})
    response.raise_for_status()
    return response


def check_correct_uac_updated_message_is_emitted_for_rops_link(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(store_all_uac_updated_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=1,
                                                      collection_exercise_id=context.collection_exercise_id))

    uac_updated_payload = context.messages_received[0]['payload']['uac']
    test_helper.assertEqual(uac_updated_payload['caseId'], context.case_details['id'],
                            'UAC updated event case ID does not match the case it was requested for')
    test_helper.assertEqual(uac_updated_payload['questionnaireId'], context.requested_qid,
                            'UAC updated event QID does not match what was submitted to R-ops')


def get_case_details_page(case_id):
    case_details_page_response = requests.get(
        f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}/case-details?case_id={case_id}')
    case_details_page_response.raise_for_status()
    return case_details_page_response
