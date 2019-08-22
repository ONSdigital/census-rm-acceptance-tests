from behave import step
from retrying import retry

from acceptance_tests.features.steps.case_look_up import get_logged_events_for_case_by_id
from acceptance_tests.utilities.test_case_helper import tc


@step("events logged against the case are {event_type_list}")
def correct_event_types_logged(context, event_type_list):
    for case in context.case_created_events:
        check_if_event_list_is_exact_match(event_type_list, case['payload']['collectionCase']['id'])


@step('"{event_type}" events are logged against the cases included in the reminder')
def check_print_case_selected_event_is_logged_against_reminder_cases(context, event_type):
    for case_id in context.reminder_case_ids:
        _check_if_event_is_logged(event_type, case_id)


@step("events logged for receipted cases are {event_type_list}")
def event_logged_for_receipting(context, event_type_list):
    actual_logged_events = get_logged_events_for_case_by_id(context.receipted_emitted_case['id'])
    check_if_event_list_is_exact_match(event_type_list, actual_logged_events)


@retry(stop_max_attempt_number=10, wait_fixed=1000)
def check_if_event_list_is_exact_match(event_type_list, case_id):
    actual_logged_events = get_logged_events_for_case_by_id(case_id)
    expected_logged_event_types = event_type_list.replace('[', '').replace(']', '').split(',')
    actual_logged_event_types = [event['eventType'] for event in actual_logged_events]

    tc.assertCountEqual(expected_logged_event_types, actual_logged_event_types,
                        msg="Actual logged event types did not match expected")


@retry(stop_max_attempt_number=10, wait_fixed=1000)
def _check_if_event_is_logged(expected_event_type, case_id):
    actual_logged_events = get_logged_events_for_case_by_id(case_id)
    actual_logged_event_types = [event['eventType'] for event in actual_logged_events]
    tc.assertEqual(actual_logged_event_types.count(expected_event_type), 1,
                   msg=(f'Expected event type = {expected_event_type},'
                        f' actual logged event types = {actual_logged_event_types}'))
