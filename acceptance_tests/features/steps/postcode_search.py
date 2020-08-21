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


@step("a user searches for cases via postcode")
def rops_search_postcode(context):
    context.postcode = context.case_created_events[0]['payload']['collectionCase']['address']['postcode']
    get_cases_from_postcode(context, context.postcode)
    context.postcode_result = requests.get(
        f'{Config.PROTOCOL}://{Config.ROPS_HOST}:{Config.ROPS_PORT}/postcode?postcode={context.postcode}')
    context.postcode_result.raise_for_status()


@step('the cases are returned to the user')
def rop_results(context):
    postcode_result_text = context.postcode_result.text
    assert f'{context.number_of_cases} results for postcode: "{context.postcode}"' in postcode_result_text
