from behave import step
from retrying import retry

from acceptance_tests.utilities.action_helper import setup_treatment_code_classified_action_rule, \
    build_and_create_action_rule, setup_address_frame_delta_action_rule
from acceptance_tests.utilities.case_api_helper import get_logged_events_for_case_by_id
from acceptance_tests.utilities.mappings import DEFAULT_CLASSIFIERS
from acceptance_tests.utilities.test_case_helper import test_helper


@step('set SPG MILITARY SFA action rule of type "{action_type}" when the case loading queues are drained')
def setup_print_action_rule_once_case_action_is_drained_spg_military_sfa(context, action_type):
    build_and_create_action_rule(context, DEFAULT_CLASSIFIERS + "estab_type = 'MILITARY SFA'", action_type)


@step('the individual response reminder action rule of type "{action_type}" is set')
def setup_print_reminder_action_rule_for_hi_cases(context, action_type):
    region_classifier = {
        'P_RL_1IRL1': "substring(region, 1, 1) = 'E'",
        'P_RL_1IRL2B': "substring(region, 1, 1) = 'W'",
    }
    build_and_create_action_rule(context, region_classifier[action_type] + " AND case_type = 'HI'", action_type)


@step('a FIELD action rule for address type "{address_type}" is set')
def create_field_action_plan(context, address_type):
    build_and_create_action_rule(context, DEFAULT_CLASSIFIERS + f"address_type = '{address_type}'", 'FIELD')


@step('set action rule of type "{action_type}" when case event "{event_type}" is logged')
def set_action_rule_when_case_event_logged(context, action_type, event_type):
    check_for_event(context, event_type)
    setup_treatment_code_classified_action_rule(context, action_type)


@retry(stop_max_attempt_number=30, wait_fixed=1000)
def check_for_event(context, event_type):
    events = get_logged_events_for_case_by_id(context.case_created_events[0]['payload']['collectionCase']['id'])

    for event in events:
        if event['eventType'] == event_type:
            return

    test_helper.fail(f"Case {context.first_case['id']} event_type {event_type} not logged")


@step('set action rule of type "{action_type}"')
def set_action_rule(context, action_type):
    setup_treatment_code_classified_action_rule(context, action_type)


@step('the address frame delta initial contact action rule of type "{action_type}" is set')
def set_address_delta_action_rule(context, action_type):
    setup_address_frame_delta_action_rule(context, action_type)
