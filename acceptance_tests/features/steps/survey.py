from behave import *
import requests
from acceptance_tests.config import Config


@given('we need a survey')
def services_running(context):
    pass


@when('we call create survey endpoint')
def create_survey(context):
    pass


@then('we get 201 response')
def validate_create_survey_response(context):
    create_survey_endpoint = f'{Config.SURVEY_SERVICE}/surveys'
    survey = {
        'surveyRef': 'Census2',
        'shortName': 'Census2',
        'longName': 'Census2',
        'legalBasisRef': 'GovERD',
        'surveyType': 'Social'}
    response = requests.post(create_survey_endpoint, auth=Config.BASIC_AUTH, json=survey)
    assert response.status_code == 201
