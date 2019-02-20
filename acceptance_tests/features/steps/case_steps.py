import json

from behave import then

from controllers.case_controller import get_cases_by_sample_unit_ids


@then("a call to the casesvc api returns {expected_case_count:d} cases")
def check_count_of_cases(context, expected_case_count):
    sample_units = [
        json.loads(sample_unit).get('id')
        for sample_unit in context.sample_units.values()
    ]
    cases = get_cases_by_sample_unit_ids(sample_units)
    assert len(cases) == expected_case_count
