import requests
from behave import given, when, then

from config import Config
from utilities.collection_exercise_utilities import create_collection_exercise
from utilities.database import reset_database
from utilities.survey_utilities import create_survey


@given('there is a live collection exercise with unique id "{unique_id}"')
def there_is_a_live_collex(context, unique_id):
    set_ids(context, unique_id)
    context.survey_id = create_survey(context.survey_ref, context.survey_ref, context.survey_ref,
                                      'GovERD', 'Social')['id']
    create_survery_classifier(context)
    context.collection_exercise_id = create_collection_exercise(context.survey_ref)


@when('a sample file "{sample_file_name}" is loaded')
def step_impl(context, sample_file_name):
    load_sample_file(sample_file_name)


@then('"{10}" Rows appear on the case database')
def step_impl(context, expected_row_count):
    # Test database table case has expected_row_count
    pass


def load_sample_file(sample_file_name):
    pass


def create_survery_classifier(context):
    post_survey_classifiers = f'{Config.SURVEY_SERVICE}/surveys/{context.survey_id}/classifiers'
    classifiers = {"name": "COLLECTION_INSTRUMENT", "classifierTypes": ["COLLECTION_EXERCISE"]}
    response = requests.post(post_survey_classifiers, auth=Config.BASIC_AUTH, json=classifiers)
    assert response.status_code == 201


def set_ids(context, scenario_id):
    # These might be for reference only?? probably just delete everything at startup,
    # but the context object should be helpful in debugging
    context.scenario_id = scenario_id
    context.survey_ref = 'Census' + context.scenario_id
    context.survey_classifiers = 'xyz'
    context.collection_exercise = 'collex' + scenario_id


@given("the database is cleared down")
def the_database_is_cleared_down(context):
    reset_database()
