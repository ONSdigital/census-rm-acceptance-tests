from behave import then

from controllers.case_controller import get_cases_by_sample_unit_ids


@then("the sample units are created and stored in the case service")
def check_count_of_cases(context):
    sample_units_ids = [
        sample_unit['id']
        for sample_unit in context.sample_units
    ]

    cases = get_cases_by_sample_unit_ids(sample_units_ids)
    assert len(cases) == len(sample_units_ids)
