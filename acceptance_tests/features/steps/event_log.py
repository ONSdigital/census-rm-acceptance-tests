from behave import step
from retrying import retry

from acceptance_tests.features.steps.case_look_up import get_logged_events_for_case_by_id


@step("events logged against the case are {event_type_list}")
def correct_event_types_logged(context, event_type_list):
    for case in context.case_created_events:
        check_if_event_list_is_exact_match(event_type_list, case['payload']['collectionCase']['id'])


@retry(stop_max_attempt_number=10, wait_fixed=1000)
def check_if_event_list_is_exact_match(event_type_list, case_id):
    actual_logged_events = get_logged_events_for_case_by_id(case_id)
    expected_logged_event_types = event_type_list.replace('[', '').replace(']', '').split(',')
    expected_logged_event_types_copy = expected_logged_event_types.copy()

    assert len(actual_logged_events) == len(expected_logged_event_types), "wrong number of events logged"

    for case_event in actual_logged_events:
        for expected_event in expected_logged_event_types:
            if case_event['eventType'] == expected_event:
                expected_logged_event_types_copy.remove(expected_event)
                break

    if len(expected_logged_event_types_copy) > 0:
        assert False, "didn't log expected event types"
