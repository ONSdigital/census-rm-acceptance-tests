from behave import step
from retrying import retry

from acceptance_tests.utilities.case_api_helper import get_logged_events_for_case_by_id
from acceptance_tests.utilities.event_helper import check_if_event_list_is_exact_match
from acceptance_tests.utilities.test_case_helper import test_helper


@step("events logged against the case are {event_type_list}")
def correct_event_types_logged(context, event_type_list):
    for case in context.case_created_events:
        check_if_event_list_is_exact_match(event_type_list, case['payload']['collectionCase']['id'])


@step('the expected number of "RM_UAC_CREATED" and {event_type_list} events are logged against the case')
def correct_event_types_logged_for_ce_estabs(context, event_type_list):
    expected_logged_event_types = event_type_list.replace('[', '').replace(']', '').split(',')
    for case in context.case_created_events:
        new_type_list = expected_logged_event_types.copy()
        for _ in range(case['payload']['collectionCase']['ceExpectedCapacity']):
            new_type_list.append('RM_UAC_CREATED')

        check_if_event_list_is_exact_match(','.join(new_type_list), case['payload']['collectionCase']['id'])


@step('two "RM_UAC_CREATED" events {event_type_list} are logged per case')
def correct_event_types_logged_for_ce_estabs_for_wales(context, event_type_list):
    # need to create both an English and Welsh UAC/QID pair for Welsh PQ cases which are identified by Treatment ID
    expected_logged_event_types = event_type_list.replace('[', '').replace(']', '').split(',')
    for case in context.case_created_events:
        new_type_list = expected_logged_event_types.copy()
        for _ in range(case['payload']['collectionCase']['ceExpectedCapacity']):
            new_type_list.append('RM_UAC_CREATED')
            if (case['payload']['collectionCase']['treatmentCode']) == 'CE_QDIEW':
                new_type_list.append('RM_UAC_CREATED')

        check_if_event_list_is_exact_match(','.join(new_type_list), case['payload']['collectionCase']['id'])


@step('"{event_type}" events are logged against the cases included in the reminder')
def check_print_case_selected_event_is_logged_against_reminder_cases(context, event_type):
    for case_id in context.reminder_case_ids:
        _check_if_event_is_logged(event_type, case_id)


@step('the events logged against the tranche 2 fieldwork cases are {event_type_list}')
def events_logged_for_fieldwork_cases(context, event_type_list):
    for case_id in context.fieldwork_case_ids:
        check_if_event_list_is_exact_match(event_type_list, case_id)


@step("the events logged for the case are {expected_event_list}")
@step("the events logged for the receipted case are {expected_event_list}")
def check_logged_events_for_emitted_case(context, expected_event_list):
    check_if_event_list_is_exact_match(expected_event_list, context.first_case['id'])


@retry(stop_max_attempt_number=10, wait_fixed=1000)
def _check_if_event_is_logged(expected_event_type, case_id):
    actual_logged_events = get_logged_events_for_case_by_id(case_id)
    actual_logged_event_types = [event['eventType'] for event in actual_logged_events]
    test_helper.assertEqual(actual_logged_event_types.count(expected_event_type), 1,
                            msg=(f'Expected event type = {expected_event_type},'
                                 f' actual logged event types = {actual_logged_event_types}'))
