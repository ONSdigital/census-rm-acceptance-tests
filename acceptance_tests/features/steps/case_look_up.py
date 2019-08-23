import json
import logging
from random import randint
from uuid import uuid4

import requests
from behave import then, given
from structlog import wrap_logger
from config import Config

logger = wrap_logger(logging.getLogger(__name__))
caseapi_url = f'{Config.CASEAPI_SERVICE}/cases/'


@then("a case can be retrieved from the case API service")
def get_case_by_id(context):
    case_id = context.case_created_events[0]['payload']['collectionCase']['id']

    response = requests.get(f'{caseapi_url}{case_id}')

    assert response.status_code == 200, 'Case not found'


@given('a random caseId is generated')
def generate_random_uuid(context):
    context.dummy_case_id = uuid4()
    context.test_endpoint_with_non_existent_value = context.dummy_case_id
    logger.info(f'Dummy caseId = {context.dummy_case_id}')


@given('a random uprn is generated')
def generate_random_uprn(context):
    context.random_uprn = randint(15000000000, 19999999999)
    context.test_endpoint_with_non_existent_value = f'uprn/{context.random_uprn}'
    logger.info(f'Dummy uprn = {context.random_uprn}')


@given('a random caseRef is generated')
def generate_random_caseref(context):
    context.random_caseref = randint(15000000, 19999999)
    context.test_endpoint_with_non_existent_value = f'ref/{context.random_caseref}'
    logger.info(f'Dummy caseRef = {context.random_caseref}')


@then('case API should return a 404 when queried')
def get_non_existent_case_id(context):
    response = requests.get(f'{caseapi_url}{context.test_endpoint_with_non_existent_value}')

    assert response.status_code == 404, 'Case returned'


@then('case API returns multiple cases for a UPRN')
def find_multiple_cases_by_uprn(context):
    response = requests.get(f'{caseapi_url}uprn/10008677190')
    response.raise_for_status()

    response_data = json.loads(response.content)

    assert len(response_data) > 1, 'Multiple cases not found'
    # Check some of the fields aren't blank
    for case in response_data:
        assert case['id'], 'caseId missing'
        assert case['caseRef'], 'caseRef missing'
        assert case['postcode'], 'postcode missing'


@then('a case can be retrieved by its caseRef')
def find_case_by_caseRef(context):
    case_ref = context.case_created_events[0]['payload']['collectionCase']['caseRef']

    response = requests.get(f'{caseapi_url}ref/{case_ref}')

    assert response.status_code == 200, 'Case ref not found'


@then('events of type "{event_type}" are logged against the case')
def correct_event_type_logged(context, event_type):
    for case in context.case_created_events:
        case_id = case['payload']['collectionCase']['id']
        response = requests.get(f'{caseapi_url}{case_id}?caseEvents=true').content.decode("utf-8")
        response_json = json.loads(response)

        for caseEvent in response_json['caseEvents']:
            if caseEvent['eventType'] == event_type:
                return
        assert False


@then("the events logged for the case are {event_type_list}")
def event_logged_for_case(context, event_type_list):
    from acceptance_tests.features.steps.event_log import check_if_event_list_is_exact_match
    check_if_event_list_is_exact_match(event_type_list, context.emitted_case['id'])


def get_logged_events_for_case_by_id(case_id):
    response = requests.get(f'{caseapi_url}{case_id}?caseEvents=true').content.decode("utf-8")
    response_json = json.loads(response)
    return response_json['caseEvents']
