from acceptance_tests.controllers.case_controller import get_cases_by_survey_id, get_1st_iac_for_case_id
from acceptance_tests.utilities.date_utilities import format_date_as_ddmm


def create_expected_csv_lines(context):
    context.sample_units = _get_iacs_and_apply_to_sample_units(context)

    return_by_date = format_date_as_ddmm(context.dates["return_by"])

    return [
        _create_expected_csv_line(expected_data, return_by_date)
        for expected_data in context.sample_units
    ]


def _create_expected_csv_line(expected_data, return_by_date):
    attributes = expected_data["attributes"]

    return (
        f'{attributes["ADDRESS_LINE1"]}:'
        f'{attributes["ADDRESS_LINE2"]}:'
        f'{attributes["POSTCODE"]}:'
        f'{attributes["TOWN_NAME"]}:'
        f'{attributes["LOCALITY"]}:'
        f'{attributes["COUNTRY"]}:'
        f'{expected_data["iac"]}:'
        f'{attributes["TLA"]}{attributes["REFERENCE"]}:'
        f'{return_by_date}'
    )


def _get_iacs_and_apply_to_sample_units(context):
    cases = get_cases_by_survey_id(context.survey_id, len(context.sample_units))

    for case in cases:
        _get_iac_and_apply_to_sample_unit(case, context.sample_units)

    return context.sample_units


def _get_iac_and_apply_to_sample_unit(case, sample_units):
    iac = get_1st_iac_for_case_id(case["id"])

    for sample_unit in sample_units:
        if case["sampleUnitId"] == sample_unit["id"]:
            sample_unit.update({'iac': iac})
            return
