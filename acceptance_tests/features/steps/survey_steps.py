from behave import given

from data_setup.action_setup import get_action_plan_id
from data_setup.collection_exercise_setup import setup_census_collection_exercise_to_scheduled_state
from data_setup.survey_setup import setup_census_survey


@given('a survey exists with collection exercise')
def a_survey_exists(context):
    setup_census_survey(context)
    setup_census_collection_exercise_to_scheduled_state(context)
    context.action_plan_id = get_action_plan_id(context.collection_exercise_id)
