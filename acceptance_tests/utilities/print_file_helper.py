from collections import defaultdict


def create_expected_csv_lines(context, prefix, ignore_case_id=None):
    expected_data = defaultdict(dict)

    for uac in context.uac_created_events:
        if ignore_case_id is None or uac['payload']['uac']['caseId'] != ignore_case_id:
            expected_data[uac['payload']['uac']['caseId']]['uac'] = uac['payload']['uac']['uac']

    for case in context.case_created_events:
        if ignore_case_id is None or case['payload']['collectionCase']['id'] != ignore_case_id:
            expected_data = _add_expected_case_data(case, expected_data)

    return [
        _create_expected_csv_line(case, prefix)
        for case in expected_data.values()
    ]


def create_expected_questionaire_csv_lines(context, prefix):
    expected_data = defaultdict(dict)

    for uac in context.uac_created_events:
        expected_data = _add_expected_uac_data(uac, expected_data)

    for case in context.case_created_events:
        expected_data = _add_expected_questionnaire_case_data(case, expected_data)

    return [
        _create_expected_questionaire_csv_line(case, prefix)
        for case in expected_data.values()
    ]


def _add_expected_uac_data(message, expected_data):
    uac_key = message['payload']['uac']['caseId']
    uac_obj = message['payload']['uac']

    if uac_obj['questionnaireId'][:2] in ('01', '02', '04'):
        expected_data[uac_key]['uac'] = uac_obj['uac']
        expected_data[uac_key]['qid'] = uac_obj['questionnaireId']
    elif uac_obj['questionnaireId'][:2] == '03':
        expected_data[uac_key]['uac_wales'] = uac_obj['uac']
        expected_data[uac_key]['qid_wales'] = uac_obj['questionnaireId']
    else:
        assert False, "Unexpected questionnaire type"

    return expected_data


def _add_expected_case_data(message, expected_data):
    case_key = message['payload']['collectionCase']['id']

    expected_data[case_key]['case_ref'] = message['payload']['collectionCase']['caseRef']

    address_obj = message['payload']['collectionCase']['address']
    expected_data[case_key]['address_line_1'] = address_obj['addressLine1']
    expected_data[case_key]['address_line_2'] = address_obj['addressLine2']
    expected_data[case_key]['address_line_3'] = address_obj['addressLine3']
    expected_data[case_key]['town_name'] = address_obj['townName']
    expected_data[case_key]['postcode'] = address_obj['postcode']

    return expected_data


def _add_expected_questionnaire_case_data(message, expected_data):
    case_key = message['payload']['collectionCase']['id']

    expected_data[case_key]['coordinator_id'] = message['payload']['collectionCase']['fieldCoordinatorId']

    address_obj = message['payload']['collectionCase']['address']
    expected_data[case_key]['address_line_1'] = address_obj['addressLine1']
    expected_data[case_key]['address_line_2'] = address_obj['addressLine2']
    expected_data[case_key]['address_line_3'] = address_obj['addressLine3']
    expected_data[case_key]['town_name'] = address_obj['townName']
    expected_data[case_key]['postcode'] = address_obj['postcode']

    return expected_data


def _create_expected_csv_line(case, prefix):
    return (
        f'{case["uac"]}|'
        f'{case["case_ref"]}|'
        f'|||'
        f'{case["address_line_1"]}|'
        f'{case["address_line_2"]}|'
        f'{case["address_line_3"]}|'
        f'{case["town_name"]}|'
        f'{case["postcode"]}|'
        f'{prefix}'
    )


def _create_expected_questionaire_csv_line(case, prefix):
    return (
        f'{case["uac"]}|'
        f'{case["qid"]}|'
        f'{case.get("uac_wales", "")}|'
        f'{case.get("qid_wales", "")}|'
        f'{case["coordinator_id"]}|'
        f'|||'
        f'{case["address_line_1"]}|'
        f'{case["address_line_2"]}|'
        f'{case["address_line_3"]}|'
        f'{case["town_name"]}|'
        f'{case["postcode"]}|'
        f'{prefix}'
    )
