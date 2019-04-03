from acceptance_tests.controllers.case_controller import get_cases_by_survey_id, get_1st_iac_for_case_id


def create_expected_csv_lines(context):
    context.sample_units = _get_case_data_and_apply_to_sample_units(context)

    return [
        _create_expected_csv_line(expected_data)
        for expected_data in context.sample_units
    ]


def _create_expected_csv_line(expected_data):
    attributes = expected_data["attributes"]

    return (
        f'{expected_data["iac"]}|'
        f'{expected_data["case_ref"]}|'
        f'{attributes["ADDRESS_LINE1"]}|'
        f'{attributes["ADDRESS_LINE2"]}|'
        f'{attributes["ADDRESS_LINE3"]}|'
        f'{attributes["TOWN_NAME"]}|'
        f'{attributes["POSTCODE"]}|'
        'P_IC_ICL1'
    )


def _get_case_data_and_apply_to_sample_units(context):
    cases = get_cases_by_survey_id(context.survey_id, len(context.sample_units))

    for case in cases:
        _get_iac_and_case_ref_and_apply_to_sample_unit(case, context.sample_units)

    return context.sample_units


def _get_iac_and_case_ref_and_apply_to_sample_unit(case, sample_units):
    iac = get_1st_iac_for_case_id(case["id"])

    for sample_unit in sample_units:
        if case["sampleUnitId"] == sample_unit["id"]:
            sample_unit.update({'iac': iac,
                                'case_ref': case['caseRef']})
            return
