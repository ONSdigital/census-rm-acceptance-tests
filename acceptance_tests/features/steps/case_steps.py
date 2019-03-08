from behave import then

from controllers.case_controller import get_cases_by_survey_id


@then("the sample units are created and stored in the case service")
def check_count_of_cases(context):
    cases = get_cases_by_survey_id(context.survey_id, len(context.sample_units))
    assert len(cases) == len(context.sample_units)
