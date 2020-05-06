from collections import defaultdict

from acceptance_tests.utilities.test_case_helper import test_helper


def create_expected_csv_lines(context, prefix, ignore_case_id=None):
    expected_data = defaultdict(dict)

    for uac in context.uac_created_events:
        if ignore_case_id is None or uac['payload']['uac']['caseId'] != ignore_case_id:
            expected_data[uac['payload']['uac']['caseId']]['uac'] = uac['payload']['uac']['uac']
            expected_data[uac['payload']['uac']['caseId']]['questionnaire_id'] \
                = uac['payload']['uac']['questionnaireId']

    for case in context.case_created_events:
        if ignore_case_id is None or case['payload']['collectionCase']['id'] != ignore_case_id:
            expected_data = _add_expected_case_data(case, expected_data)

    return [
        _create_expected_csv_line(case, prefix)
        for case in expected_data.values()
    ]


def create_expected_csv_lines_for_ce_estab_responses(context, prefix):
    result = []
    for event in context.case_created_events:
        case = {}
        collection_case = get_case_details_for_CE_Estab_responses(case, event)
        for uac in context.uac_created_events:
            if uac['payload']['uac']['caseId'] == collection_case['id']:
                case['uac'] = uac['payload']['uac']['uac']
                case['questionnaire_id'] = uac['payload']['uac']['questionnaireId']
                result.append(_create_expected_csv_line(case, prefix))

    return result


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


def create_expected_CE_Estab_questionnaire_csv_lines(context, prefix):
    result = []
    expected_data = defaultdict(dict)

    for event in context.case_created_events:
        case = {}
        collection_case = get_case_details_for_CE_Estab_responses(case, event)
        for uac in context.uac_created_events:
            case_id = collection_case['id']
            if uac['payload']['uac']['caseId'] == case_id:
                if uac['payload']['uac']['questionnaireId'].startswith('23'):
                    expected_data[case_id]['uac_wales'] = uac['payload']['uac']['uac']
                    expected_data[case_id]['qid_wales'] = uac['payload']['uac']['questionnaireId']

                else:
                    expected_data[case_id]['uac'] = uac['payload']['uac']['uac']
                    expected_data[case_id]['qid'] = uac['payload']['uac']['questionnaireId']

        result.append(_create_expected_questionnaire_csv_line(case, prefix))

    return result


def get_case_details_for_CE_Estab_responses(case, event):
    collection_case = event['payload']['collectionCase']
    address = collection_case['address']
    case['address_line_1'] = address['addressLine1']
    case['address_line_2'] = address['addressLine2']
    case['address_line_3'] = address['addressLine3']
    case['town_name'] = address['townName']
    case['postcode'] = address['postcode']
    case['organization_name'] = address['organisationName']
    case['case_ref'] = collection_case['caseRef']
    case['coordinator_id'] = collection_case['fieldCoordinatorId']
    case['officer_id'] = collection_case['fieldOfficerId']
    return collection_case


def create_expected_reminder_letter_csv_lines(context, pack_code):
    expected_data = defaultdict(dict)

    expected_reminder_case_created_events = (case for case in context.case_created_events
                                             if case['payload']['collectionCase']['id'] in context.reminder_case_ids)

    for uac in context.reminder_uac_updated_events:
        expected_data[uac['payload']['uac']['caseId']]['uac'] = uac['payload']['uac']['uac']
        expected_data[uac['payload']['uac']['caseId']]['questionnaire_id'] = uac['payload']['uac']['questionnaireId']

    for case in expected_reminder_case_created_events:
        expected_data = _add_expected_case_data(case, expected_data)

    return [
        _create_expected_csv_line(case, pack_code)
        for case in expected_data.values()
    ]


def create_expected_reminder_questionnaire_csv_lines(context, pack_code):
    expected_data = defaultdict(dict)

    expected_reminder_case_created_events = (case for case in context.case_created_events
                                             if case['payload']['collectionCase']['id'] in context.reminder_case_ids)

    for uac in context.reminder_uac_updated_events:
        if not uac['payload']['uac']['questionnaireId'].startswith('03'):
            expected_data[uac['payload']['uac']['caseId']]['uac'] = uac['payload']['uac']['uac']
            expected_data[uac['payload']['uac']['caseId']]['qid'] = uac['payload']['uac']['questionnaireId']
        elif not expected_data[uac['payload']['uac']['caseId']].get('uac_wales'):
            expected_data[uac['payload']['uac']['caseId']]['uac_wales'] = uac['payload']['uac']['uac']
            expected_data[uac['payload']['uac']['caseId']]['qid_wales'] = uac['payload']['uac']['questionnaireId']
        else:
            test_helper.fail('Too many reminder UAC Updated events for case')

    for case in expected_reminder_case_created_events:
        expected_data = _add_expected_questionnaire_case_data(case, expected_data)

    return [
        _create_expected_questionnaire_csv_line(case, pack_code)
        for case in expected_data.values()
    ]


def _add_expected_uac_data(message, expected_data):
    case_id = message['payload']['uac']['caseId']
    uac_payload = message['payload']['uac']

    if uac_payload['questionnaireId'][:2] in ('01', '02', '04', '21', '22', '24'):
        expected_data[case_id]['uac'] = uac_payload['uac']
        expected_data[case_id]['qid'] = uac_payload['questionnaireId']
    elif uac_payload['questionnaireId'][:2] == '03':
        expected_data[case_id]['uac_wales'] = uac_payload['uac']
        expected_data[case_id]['qid_wales'] = uac_payload['questionnaireId']
    else:
        test_helper.fail('Unexpected questionnaire type')

    return expected_data


def _add_expected_case_data(message, expected_data):
    case_id = message['payload']['collectionCase']['id']

    collection_case = message['payload']['collectionCase']
    expected_data[case_id]['case_ref'] = collection_case['caseRef']
    expected_data[case_id]['coordinator_id'] = collection_case['fieldCoordinatorId']
    expected_data[case_id]['officer_id'] = collection_case['fieldOfficerId']

    _populate_expected_address(case_id, expected_data, message)

    return expected_data


def _add_expected_questionnaire_case_data(message, expected_data):
    case_id = message['payload']['collectionCase']['id']

    expected_data[case_id]['coordinator_id'] = message['payload']['collectionCase']['fieldCoordinatorId']
    expected_data[case_id]['officer_id'] = message['payload']['collectionCase']['fieldOfficerId']

    _populate_expected_address(case_id, expected_data, message)

    return expected_data


def _populate_expected_address(case_id, expected_data, message):
    address = message['payload']['collectionCase']['address']
    expected_data[case_id]['address_line_1'] = address['addressLine1']
    expected_data[case_id]['address_line_2'] = address['addressLine2']
    expected_data[case_id]['address_line_3'] = address['addressLine3']
    expected_data[case_id]['town_name'] = address['townName']
    expected_data[case_id]['postcode'] = address['postcode']
    expected_data[case_id]['organization_name'] = address['organisationName']


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
        f'{prefix}|'
        f'{case["questionnaire_id"]}|'
        f'{case["organization_name"]}|'
        f'{case["coordinator_id"]}|'
        f'{case["officer_id"]}'
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
        f'{prefix}|'
        f'{case["organization_name"]}|'
        f'{case["officer_id"]}'
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
        f'{pack_code}||'
    )


def create_expected_on_request_fulfilment_questionnaire_csv(context, pack_code):
    print_lines = []
    for caze in context.requested_uac_and_qid:
        print_lines.append(_create_expected_on_request_fulfilment_questionnaire_csv_line(caze['case'], pack_code,
                                                                                         caze['uac'], caze['qid']))
    return print_lines


def _create_expected_on_request_fulfilment_questionnaire_csv_line(case, pack_code, uac, qid):
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
        f'{pack_code}||'
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
        f'{fulfilment_code}||||'
    )


def create_expected_individual_response_csv(individual_case, uac, qid, fulfilment_code):
    return (
        f'{uac}|'
        f'{qid}'
        f'||||'
        f'Ms|jo|smith|'
        f'{individual_case["addressLine1"]}|'
        f'{individual_case["addressLine2"]}|'
        f'{individual_case["addressLine3"]}|'
        f'{individual_case["townName"]}|'
        f'{individual_case["postcode"]}|'
        f'{fulfilment_code}||'
    )
