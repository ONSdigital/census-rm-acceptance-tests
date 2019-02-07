from behave import *
import requests
from config import Config


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
        'surveyRef': 'Census3',
        'shortName': 'Census3',
        'longName': 'Census3',
        'legalBasisRef': 'GovERD',
        'surveyType': 'Social'}
    response = requests.post(create_survey_endpoint, auth=Config.BASIC_AUTH, json=survey)
    assert response.status_code == 201


@given("we have a survey")
def step_impl(context):
    get_survey_byref_endpoint = f'{Config.SURVEY_SERVICE}/surveys/ref/Census3'
    response = requests.get(get_survey_byref_endpoint, auth=Config.BASIC_AUTH)
    assert response.status_code == 200
    context.survey_id = response.json()['id']


@when("we add classifiers")
def step_impl(context):
    post_survey_classifiers = f'{Config.SURVEY_SERVICE}/surveys/{context.survey_id}/classifiers'
    classifiers = {"name": "COLLECTION_INSTRUMENT", "classifierTypes": ["COLLECTION_EXERCISE"]}
    response = requests.post(post_survey_classifiers, auth=Config.BASIC_AUTH, json=classifiers)
    assert response.status_code == 201


@then("we can load classifiers by survey")
def step_impl(context):
    list_survey_classifiers = f'{Config.SURVEY_SERVICE}/surveys/{context.survey_id}/classifiertypeselectors'
    response = requests.get(list_survey_classifiers, auth=Config.BASIC_AUTH)
    assert response.status_code == 200
