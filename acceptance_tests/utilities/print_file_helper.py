from collections import defaultdict

from acceptance_tests.controllers.case_controller import get_cases_by_survey_id, get_1st_iac_for_case_id


def create_expected_csv_lines(context):
    actual_data = defaultdict(dict)

    for message in context.messages_received:
        if message['event']['type'] == 'UAC_UPDATED':
            actual_data[message['payload']['uac']['caseId']]['uac'] = message['payload']['uac']['uac']
        elif message['event']['type'] == 'CASE_CREATED':
            actual_data[message['payload']['collectionCase']['id']]['case_ref'] = message['payload']['collectionCase'][
                'caseRef']
            actual_data[message['payload']['collectionCase']['id']]['address_line_1'] = \
                message['payload']['collectionCase']['address']['addressLine1']
            actual_data[message['payload']['collectionCase']['id']]['address_line_2'] = \
                message['payload']['collectionCase']['address']['addressLine2']
            actual_data[message['payload']['collectionCase']['id']]['address_line_3'] = \
                message['payload']['collectionCase']['address']['addressLine3']
            actual_data[message['payload']['collectionCase']['id']]['town_name'] = \
                message['payload']['collectionCase']['address']['townName']
            actual_data[message['payload']['collectionCase']['id']]['postcode'] = \
                message['payload']['collectionCase']['address']['postcode']

    return [
        _create_expected_csv_line(case)
        for case in actual_data.values()
    ]


def _create_expected_csv_line(case):
    return (
        f'{case["uac"]}|'
        f'{case["case_ref"]}|'
        f'{case["address_line_1"]}|'
        f'{case["address_line_2"]}|'
        f'{case["address_line_3"]}|'
        f'{case["town_name"]}|'
        f'{case["postcode"]}|'
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
