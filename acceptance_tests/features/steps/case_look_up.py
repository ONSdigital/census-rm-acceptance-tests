import json
import logging
import requests

from random import randint
from uuid import uuid4
from behave import then, given
from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))

caseapi_url = f'{Config.CASEAPI_SERVICE}/cases/'


@then('a case can be retrieved from the caseapi service')
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


@then('caseapi should return a 404 when queried')
def get_non_existent_case_id(context):
    response = requests.get(f'{caseapi_url}{context.test_endpoint_with_non_existent_value}')

    assert response.status_code == 404, 'Case returned'


@then('caseapi returns multiple cases for a UPRN')
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


@then('events of pack code "{pack_code}" are logged against the case')
def check_case_events(context, pack_code):
    for case in context.case_created_events:
        case_id = case['payload']['collectionCase']['id']
        response = requests.get(f'{caseapi_url}{case_id}?caseEvents=true').content.decode("utf-8")
        response_json = json.loads(response)

        for caseEvent in response_json['caseEvents']:
            if caseEvent['eventType'] == 'PRINT_CASE_SELECTED':
                return
        assert False


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


@then("events logged against the case are {event_type_list}")
def correct_event_types_logged(context, event_type_list):
    expected_logged_event_types = event_type_list.replace('[', '').replace(']', '').split(',')

    for case in context.case_created_events:
        expected_logged_event_types_copy = expected_logged_event_types.copy()
        case_id = case['payload']['collectionCase']['id']
        response = requests.get(f'{caseapi_url}{case_id}?caseEvents=true').content.decode("utf-8")
        response_json = json.loads(response)

        actual_logged_events = response_json['caseEvents']

        assert len(actual_logged_events) == len( expected_logged_event_types ), "wrong number of events logged"

        for case_event in actual_logged_events:
            for index, expected_event in enumerate(expected_logged_event_types):
                type = case_event['eventType']
                if case_event['eventType'] == expected_event:
                    del expected_logged_event_types_copy[index]
                    continue

        if len(expected_logged_event_types_copy) > 0:
            assert False, "didn't log expected event types"


    # any useful test here?
    assert True