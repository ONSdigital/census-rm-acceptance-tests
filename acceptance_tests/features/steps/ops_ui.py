import requests
from behave import step

from config import Config


@step("a user is on the r-ops-ui home page ready to search")
def rops_home_page(context):
    home_page_response = requests.get(f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}')
    home_page_response.raise_for_status()
    home_text = home_page_response.text
    assert 'Enter a postcode' in home_text


def get_cases_from_postcode(context, postcode):
    response = requests.get(f"{Config.CASE_API_CASE_URL}/postcode/{postcode}")
    response_json = response.json()
    context.number_of_cases = len(response_json)


@step("the user can see all case details for chosen case")
@step("the user can see all case details for chosen case except for the RM_UAC_CREATED event")
def rops_case_details_page(context):
    context.case_details = context.case_created_events[0]['payload']['collectionCase']
    case_details_page_response = requests.get(
        f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}/case-details?case_id={context.first_case["id"]}')
    case_details_page_response.raise_for_status()
    case_details_text = case_details_page_response.text

    assert context.case_details["caseRef"] in case_details_text
    assert context.case_details["address"]["addressLevel"] in case_details_text
    assert context.case_details["caseType"] in case_details_text
    assert str(context.case_details["skeleton"]) in case_details_text
    assert context.case_details["collectionExerciseId"] in case_details_text
    assert context.case_details["lsoa"] in case_details_text
    assert "RM_UAC_CREATED" not in case_details_text


@step("a user searches for cases via postcode")
@step("a user has searched for cases")
def rops_search_postcode(context):
    context.postcode = context.case_created_events[0]['payload']['collectionCase']['address']['postcode']
    get_cases_from_postcode(context, context.postcode)
    context.postcode_result = requests.get(
        f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}/postcode?postcode={context.postcode}')
    context.postcode_result.raise_for_status()


@step('the cases are returned to the user')
def rops_results(context):
    postcode_result_text = context.postcode_result.text
    assert f'{context.number_of_cases} results for postcode: "{context.postcode}"' in postcode_result_text
