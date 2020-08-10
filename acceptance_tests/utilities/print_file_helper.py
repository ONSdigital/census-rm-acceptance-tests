import copy
import logging
from collections import defaultdict

from retrying import retry
from structlog import wrap_logger

from acceptance_tests.utilities.sftp_utility import SftpUtility
from acceptance_tests.utilities.test_case_helper import test_helper

logger = wrap_logger(logging.getLogger(__name__))

ICL_PACKCODES_WHICH_ARE_SORTED = [
    'D_CE1A_ICLCR1', 'D_CE1A_ICLCR2B', 'D_ICA_ICLR1', 'D_ICA_ICLR1',
    'D_ICA_ICLR2B', 'D_ICA_ICLR2B', 'D_CE4A_ICLR4', 'D_CE4A_ICLS4'
]

ICL_TEMPLATE_FIELD_OFFICER_COLUMN = 14
ICL_TEMPLATE_ORGANISATION_COLUMN = 12

QM_PACKCODES_WHICH_ARE_SORTED = ['D_FDCE_I1', 'D_FDCE_I2', 'D_FDCE_I4', 'D_FDCE_H1', 'D_FDCE_H2']
QM_TEMPLATE_FIELD_OFFICER_COLUMN = 15
QM_TEMPLATE_ORGANISATION_COLUMN = 14


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


def create_expected_csv_lines_with_no_uac_for_reminder_survey_launched(context, prefix, expected_case_ids=None):
    expected_data = defaultdict(dict)

    for case in context.case_created_events:
        if case['payload']['collectionCase']['id'] in expected_case_ids:
            expected_data = _add_expected_case_data(case, expected_data)
            case_id = case['payload']['collectionCase']['id']
            # We blank out the uac & qid rows because these are not sent on the reminder - respondent already has a UAC
            expected_data[case_id]['uac'] = ''
            expected_data[case_id]['questionnaire_id'] = ''

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
    for event in context.case_created_events:
        case = {}
        collection_case = get_case_details_for_CE_Estab_responses(case, event)
        for uac in context.uac_created_events:
            if uac['payload']['uac']['caseId'] == collection_case['id']:
                case['uac'] = uac['payload']['uac']['uac']
                case['qid'] = uac['payload']['uac']['questionnaireId']
                result.append(_create_expected_questionnaire_csv_line(case, prefix))

    return result


def create_expected_Welsh_CE_Estab_questionnaire_csv_line_endings(context, prefix):
    # creates dictionary of case details and expected 'line_ending'
    # for use when we do not know the value of the UAC/QID pairs

    case_expected_line_endings = {}

    for event in context.case_created_events:
        case = {}
        collection_case = get_case_details_for_CE_Estab_responses(case, event)
        case_expected_line_endings[collection_case['id']] = {}

        case_expected_line_endings[collection_case['id']]['line_ending'] = \
            _create_expected_questionnaire_csv_line_ending_for_welsh_ce_individual_estab_case(case, prefix)
        case_expected_line_endings[collection_case['id']]['case_details'] = collection_case

    return case_expected_line_endings


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


def create_expected_individual_reminder_letter_csv_lines(context, pack_code):
    expected_data = defaultdict(dict)

    expected_reminder_case_created_events = (case for case in context.case_created_events
                                             if case['payload']['collectionCase']['id'] in context.reminder_case_ids)

    for case in expected_reminder_case_created_events:
        expected_data = _add_expected_individual_case_data(case, expected_data)

    return [
        _create_expected_individual_reminder_csv_line(case, pack_code)
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


def _add_expected_individual_case_data(message, expected_data):
    case_id = message['payload']['collectionCase']['id']

    collection_case = message['payload']['collectionCase']
    expected_data[case_id]['case_ref'] = collection_case['caseRef']

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


def _create_expected_individual_reminder_csv_line(case, prefix):
    return (
        '|'
        f'{case["case_ref"]}|'
        '|||'
        f'{case["address_line_1"]}|'
        f'{case["address_line_2"]}|'
        f'{case["address_line_3"]}|'
        f'{case["town_name"]}|'
        f'{case["postcode"]}|'
        f'{prefix}|'
        '|'
        f'{case["organization_name"]}|'
        '|'
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


def _create_expected_questionnaire_csv_line_ending_for_welsh_ce_individual_estab_case(case, prefix):
    return (
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


def create_expected_HH_UAC_supplementary_materials_csv(context, fulfilment_code):
    return [_create_expected_HH_UAC_supplementary_materials_csv_line(context.first_case, context.requested_uac,
                                                                     context.requested_qid, fulfilment_code)]


def create_expected_CE_UAC_supplementary_materials_csv(context, fulfilment_code):
    return [create_CE_uac_print_materials_csv_line(context.first_case, context.requested_uac,
                                                   context.requested_qid, fulfilment_code)]


def _create_expected_HH_UAC_supplementary_materials_csv_line(case, uac, qid, fulfilment_code):
    return (
        f'{uac}|{case["caseRef"]}|'
        f'|||'
        f'{case["address"]["addressLine1"]}|'
        f'{case["address"]["addressLine2"]}|'
        f'{case["address"]["addressLine3"]}|'
        f'{case["address"]["townName"]}|'
        f'{case["address"]["postcode"]}|'
        f'{fulfilment_code}|{qid}|||'
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


def create_uac_print_materials_csv_line(individual_case, uac, qid, fulfilment_code):
    return (
        f'{uac}|{individual_case["caseRef"]}|'
        f'Ms|jo|smith|'
        f'{individual_case["addressLine1"]}|'
        f'{individual_case["addressLine2"]}|'
        f'{individual_case["addressLine3"]}|'
        f'{individual_case["townName"]}|'
        f'{individual_case["postcode"]}|'
        f'{fulfilment_code}|{qid}|||'
    )


def create_CE_uac_print_materials_csv_line(case, uac, qid, fulfilment_code):
    return (
        f'{uac}|{case["caseRef"]}|'
        f'Ms|jo|smith|'
        f'{case["address"]["addressLine1"]}|'
        f'{case["address"]["addressLine2"]}|'
        f'{case["address"]["addressLine3"]}|'
        f'{case["address"]["townName"]}|'
        f'{case["address"]["postcode"]}|'
        f'{fulfilment_code}|{qid}|||'
    )


def create_individual_print_material_csv_line_for_spg_ce(case, uac, qid, fulfilment_code):
    return (
        f'{uac}|'
        f'{qid}'
        f'||||'
        f'Ms|jo|smith|'
        f'{case["address"]["addressLine1"]}|'
        f'{case["address"]["addressLine2"]}|'
        f'{case["address"]["addressLine3"]}|'
        f'{case["address"]["townName"]}|'
        f'{case["address"]["postcode"]}|'
        f'{fulfilment_code}||'
    )


def check_print_files_have_all_the_expected_data(context, expected_csv_lines, pack_code):
    with SftpUtility() as sftp_utility:
        _validate_print_file_content(context, sftp_utility, context.test_start_local_datetime, expected_csv_lines,
                                     pack_code)


@retry(retry_on_exception=lambda e: isinstance(e, FileNotFoundError), wait_fixed=1000, stop_max_attempt_number=120)
def _validate_print_file_content(context, sftp_utility, start_of_test, expected_csv_lines, pack_code):
    logger.debug('Checking for files on SFTP server')

    context.expected_print_files = sftp_utility.get_all_files_after_time(start_of_test, pack_code, ".csv.gpg")

    actual_content_list = sftp_utility.get_files_content_as_list(context.expected_print_files, pack_code)
    if not actual_content_list:
        raise FileNotFoundError

    unsorted_actual_content_list = copy.deepcopy(actual_content_list)
    actual_content_list.sort()
    expected_csv_lines.sort()

    test_helper.assertEquals(actual_content_list, expected_csv_lines, 'Print file contents did not match expected')

    if pack_code in ICL_PACKCODES_WHICH_ARE_SORTED or pack_code in QM_PACKCODES_WHICH_ARE_SORTED:
        _check_actual_file_contents_sorted_by_production_code(unsorted_actual_content_list, pack_code)


def _check_actual_file_contents_sorted_by_production_code(unsorted_actual_content_list, pack_code):
    # If this was split over multiple files it could fail, not expected with current testing
    # produce a list of split_csv rows to sort
    split_csv_rows = [
        csvrow.split("|")
        for csvrow in unsorted_actual_content_list
    ]

    # If called with an invalid packcode the test will fail, this is expected behaviour
    sorted_list = []

    # This will sort a list of lists based on template ICL or QM
    # in both cases we're sorting by field_officer_id and org_name
    if pack_code in ICL_PACKCODES_WHICH_ARE_SORTED:
        sorted_list = sorted(split_csv_rows, key=lambda row: (row[ICL_TEMPLATE_FIELD_OFFICER_COLUMN],
                                                              row[ICL_TEMPLATE_ORGANISATION_COLUMN]))
    elif pack_code in QM_PACKCODES_WHICH_ARE_SORTED:
        sorted_list = sorted(split_csv_rows, key=lambda row: (row[QM_TEMPLATE_FIELD_OFFICER_COLUMN],
                                                              row[QM_TEMPLATE_ORGANISATION_COLUMN]))

    # Turn back to a list of expected_csv rows
    expected_csv_rows = [
        '|'.join(row)
        for row in sorted_list
    ]

    test_helper.assertEquals(unsorted_actual_content_list, expected_csv_rows,
                             'Sorted file contents did not match expected')
