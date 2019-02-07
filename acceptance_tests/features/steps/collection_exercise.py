from behave import *
from utilities import survey_utilities, collection_exercise_utilities


event_keys = ["mps", "go_live", "ref_period_start", "ref_period_end", "return_by", "reminder", "reminder2",
              "reminder3", "employment", "exercise_end"]

mandatory_event_keys = ["mps", "go_live", "return_by", "exercise_end"]


@given("a survey exists")
def step_impl(context):
    response = survey_utilities.create_survey(survey_ref='Census', short_name='Census', long_name='Census')
    context.survey_id = response['id']


@when("we create a collection exercise")
def step_impl(context):
    response = collection_exercise_utilities.create_collection_exercise(survey_id=context.survey_id, exercise_ref="C1", user_description= "Census Exercise 1")


@then("collection exercise id is created")
def step_impl(context):
    pass
