import json

from behave import then

from controllers.case_controller import get_cases_by_sample_unit_ids


@then("the sample units are created and stored in the case service")
def check_count_of_cases(context):
    sample_units = [
        json.loads(sample_unit).get('id')
        for sample_unit in context.sample_units.values()
    ]
    cases = get_cases_by_sample_unit_ids(sample_units)
    assert len(cases) == len(sample_units)
