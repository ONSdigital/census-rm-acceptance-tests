import json
import logging
import requests

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
    logger.info(f'Dummy caseId = {context.dummy_case_id}')


@then('caseapi should return an empty list when queried')
def get_non_existent_case_id(context):
    response = requests.get(f'{caseapi_url}{context.dummy_case_id}')

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
