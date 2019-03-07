from datetime import datetime

from behave import given

from data_setup.action_setup import create_action_plan
from data_setup.collection_exercise_setup import setup_census_collection_exercise
from data_setup.survey_setup import setup_census_survey


@given('a survey exists with a collection exercise')
def a_survey_exists_with_collex(context):
    context.test_start_datetime = datetime.utcnow()
    setup_census_survey(context)
    setup_census_collection_exercise(context)
    context.action_plan_id = create_action_plan(context.survey_ref, context.collection_exercise_id)

