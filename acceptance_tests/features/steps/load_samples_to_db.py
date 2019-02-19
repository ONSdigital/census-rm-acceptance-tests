import json

from behave import given, when, then

from setup.action_setup import setup_action_plan
from setup.collection_exercise_setup import setup_census_collection_exercise_to_scheduled_state
from setup.survey_setup import setup_census_survey
from utilities.case import get_all_cases_from_casesvc
from utilities.sample_loader.sample_file_loader import load_sample_file


@given('a survey exists')
def a_survey_exists(context):
    setup_census_survey(context)


@given('a collection exercise exists in a scheduled state')
def a_collection_exercise_exists_in_a_scheduled_state(context):
    setup_census_collection_exercise_to_scheduled_state(context)


@given('a Social Notification action plan exists')
def a_social_Notification_action_plan_exists(context):
    action_response, context.action_plan_id = setup_action_plan(context.survey_ref, context.collection_exercise_id,
                                                                 'SOCIALNOT')


@when('a sample file "{sample_file_name}" is loaded')
def load_sample_file_step(context, sample_file_name):
    sample_file_path = f'./resources/sample_files/{sample_file_name}'

    context.sample_file_name = sample_file_path
    context.sample_units = load_sample_file(context)


@then("a call to the casesvc api returns {expected_row_count:d} cases")
def check_count_of_cases(context, expected_row_count):
    sample_units = [
        json.loads(sample_unit).get('id')
        for sample_unit in context.sample_units.values()
    ]

    cases_response = get_all_cases_from_casesvc(sample_units)

    assert len(cases_response) == expected_row_count
