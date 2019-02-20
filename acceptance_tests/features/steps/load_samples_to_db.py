import json

from behave import given, when, then

from controllers.case_controller import get_cases_by_sample_unit_ids
from data_setup.action_setup import get_action_plan_id
from data_setup.collection_exercise_setup import setup_census_collection_exercise_to_scheduled_state
from data_setup.survey_setup import setup_census_survey
from utilities.sample_loader.sample_file_loader import load_sample_file


@given('a survey exists')
def a_survey_exists(context):
    setup_census_survey(context)


@given('a collection exercise exists in a scheduled state')
def a_collection_exercise_exists_in_a_scheduled_state(context):
    setup_census_collection_exercise_to_scheduled_state(context)


@given('a social action plan exists for the collection exercise')
def a_social_action_plan_exists(context):
    context.action_plan_id = get_action_plan_id(context.collection_exercise_id)


@when('a sample file "{sample_file_name}" is loaded')
def load_sample_file_step(context, sample_file_name):
    context.sample_file_name = f'./resources/sample_files/{sample_file_name}'
    context.sample_units = load_sample_file(context)


@then("a call to the casesvc api returns {expected_case_count:d} cases")
def check_count_of_cases(context, expected_case_count):
    sample_units = [
        json.loads(sample_unit).get('id')
        for sample_unit in context.sample_units.values()
    ]
    cases = get_cases_by_sample_unit_ids(sample_units)
    assert len(cases) == expected_case_count
