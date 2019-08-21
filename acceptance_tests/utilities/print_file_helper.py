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


def create_expected_questionnaire_csv_lines(context, prefix):
    expected_data = defaultdict(dict)

    for uac in context.uac_created_events:
        expected_data = _add_expected_uac_data(uac, expected_data)

    for case in context.case_created_events:
        expected_data = _add_expected_questionnaire_case_data(case, expected_data)

    return [
        _create_expected_questionnaire_csv_line(case, prefix)
        for case in expected_data.values()
    ]


def _add_expected_uac_data(message, expected_data):
    case_id = message['payload']['uac']['caseId']
    uac_payload = message['payload']['uac']

    if uac_payload['questionnaireId'][:2] in ('01', '02', '04'):
        expected_data[case_id]['uac'] = uac_payload['uac']
        expected_data[case_id]['qid'] = uac_payload['questionnaireId']
    elif uac_payload['questionnaireId'][:2] == '03':
        expected_data[case_id]['uac_wales'] = uac_payload['uac']
        expected_data[case_id]['qid_wales'] = uac_payload['questionnaireId']
    else:
        assert False, "Unexpected questionnaire type"

    return expected_data


def _add_expected_case_data(message, expected_data):
    case_id = message['payload']['collectionCase']['id']

    expected_data[case_id]['case_ref'] = message['payload']['collectionCase']['caseRef']

    _populate_expected_address(case_id, expected_data, message)

    return expected_data


def _add_expected_questionnaire_case_data(message, expected_data):
    case_id = message['payload']['collectionCase']['id']

    expected_data[case_id]['coordinator_id'] = message['payload']['collectionCase']['fieldCoordinatorId']

    _populate_expected_address(case_id, expected_data, message)

    return expected_data


def _populate_expected_address(case_id, expected_data, message):
    address = message['payload']['collectionCase']['address']
    expected_data[case_id]['address_line_1'] = address['addressLine1']
    expected_data[case_id]['address_line_2'] = address['addressLine2']
    expected_data[case_id]['address_line_3'] = address['addressLine3']
    expected_data[case_id]['town_name'] = address['townName']
    expected_data[case_id]['postcode'] = address['postcode']


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


def _create_expected_questionnaire_csv_line(case, prefix):
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


def create_expected_on_request_questionnaire_csv(context, pack_code):
    return [_create_expected_on_request_questionnaire_csv_line(context.first_case, pack_code,
                                                               context.requested_uac,
                                                               context.requested_qid)]


def _create_expected_on_request_questionnaire_csv_line(case, pack_code, uac, qid):
    return (
        f'{uac}|'
        f'{qid}'
        f'||||'
        f'Mrs|Test|McTest|'
        f'{case["address"]["addressLine1"]}|'
        f'{case["address"]["addressLine2"]}|'
        f'{case["address"]["addressLine3"]}|'
        f'{case["address"]["townName"]}|'
        f'{case["address"]["postcode"]}|'
        f'{pack_code}'
    )


def create_expected_supplementary_materials_csv(context, fulfilment_code):
    return [_create_expected_supplementary_materials_csv_line(context.first_case, fulfilment_code)]


def _create_expected_supplementary_materials_csv_line(case, fulfilment_code):
    return (
        f'|{case["caseRef"]}|'
        f'Mrs|Test|McTest|'
        f'{case["address"]["addressLine1"]}|'
        f'{case["address"]["addressLine2"]}|'
        f'{case["address"]["addressLine3"]}|'
        f'{case["address"]["townName"]}|'
        f'{case["address"]["postcode"]}|'
        f'{fulfilment_code}'
    )
