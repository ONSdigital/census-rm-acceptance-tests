import requests

from acceptance_tests.config import Config

def setup_collection_exercise_and_dependencies(context, scenario_id):
    set_ids(scenario_id, context)
    create_survey(context)
    create_survery_classifier(context)
    create_collection_exercise(context)


def create_survey(scenario_id):
    census_ref = 'Census' + scenario_id

    create_survey_endpoint = f'{Config.SURVEY_SERVICE}/surveys'
    survey = {
        'surveyRef': 'Census2',
        'shortName': 'Census2',
        'longName': 'Census2',
        'legalBasisRef': 'GovERD',
        'surveyType': 'Social'}
    response = requests.post(create_survey_endpoint, auth=Config.BASIC_AUTH, json=survey)
    assert response.status_code == 201

    return census_ref


def create_survery_classifier(context):
    # setup survey classifier
    return 'survey classifier'


def create_collection_exercise(context):
    return 'new collection exercise id'


def teardown_whole_collection_exercise(scenario_id, context):
    # Create all of the ids for each part and then via DB remove them?
    # This suggests to me that we should consider having a shared function to set all of these values, no point in repeating ourselves.

    set_ids(context, scenario_id)

    #Then delete what we don't want

def set_ids(context, scenario_id):
    context.scenario_id = scenario_id
    context..survey_id = 'survery' + scenario_id
    context.survey_classerfiers = 'xyz'
    context.collection_exercise = 'collex' + scenario_id