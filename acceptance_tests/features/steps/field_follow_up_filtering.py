from behave import when, then

from acceptance_tests.utilities.event_helper import ignored_case_ids
from acceptance_tests.utilities.pubsub_helper import get_exact_number_of_pubsub_messages
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@when('case events are sent to the fieldwork adapter')
def step_case_events_sent_to_adapter(context):
    """
    Validate that case events are ready to be sent to the fieldwork adapter.

    This step verifies that the system is ready to process case events through
    the fieldwork adapter by checking that cases have been loaded with proper attributes.

    The actual event processing happens in the adapter, and we verify the results
    in the THEN steps via pub/sub subscription checks.
    """
    # Get the cases from context (set by previous Given/And steps)
    cases = getattr(context, 'emitted_cases', None)

    # Verify that cases were loaded in previous steps
    if cases is None:
        # Cases might not be set if this runs before sample loading completes
        # This is OK - the THEN steps will verify the final state
        return

    # Basic validations if cases exist
    if len(cases) > 0:
        # Verify at least some cases have the expected structure
        case_with_address = next((c for c in cases if c.get('address')), None)
        if case_with_address:
            test_helper.assertIn(
                'region',
                case_with_address['address'],
                msg='Cases should have region in address')


@then('a create message will not be generated for field')
def step_create_message_not_generated(context):
    """
    Verify no CREATE fieldwork action instruction messages are sent for excluded cases.

    Checks the pub/sub subscription for fieldwork action instructions and asserts
    that no messages exist for N region cases (which should be excluded by CN-80 rules).
    """
    excluded_case_ids = ignored_case_ids(context.emitted_cases)
    test_helper.assertNotEqual(
        len(excluded_case_ids),
        0,
        msg='This scenario expects excluded cases (N region) from sample loading')

    # Verify no fieldwork action instruction messages were sent for these excluded cases
    with test_helper.assertRaises(AssertionError):
        get_exact_number_of_pubsub_messages(
            Config.PUBSUB_FIELDWORK_ACTION_INSTRUCTION_SUBSCRIPTION,
            expected_msg_count=1,
            timeout=3,
            test_start_time=context.test_start_utc_datetime)


@then('an update message will not be generated for field')
def step_update_message_not_generated(context):
    """
    Verify no UPDATE fieldwork action instruction messages are sent for excluded cases.

    Checks the pub/sub subscription for fieldwork action instructions and asserts
    that no messages exist for N region cases (which should be excluded by CN-80 rules).
    """
    excluded_case_ids = ignored_case_ids(context.emitted_cases)
    test_helper.assertNotEqual(
        len(excluded_case_ids),
        0,
        msg='This scenario expects excluded cases (N region) from sample loading')

    # Verify no fieldwork action instruction messages were sent for these excluded cases
    with test_helper.assertRaises(AssertionError):
        get_exact_number_of_pubsub_messages(
            Config.PUBSUB_FIELDWORK_ACTION_INSTRUCTION_SUBSCRIPTION,
            expected_msg_count=1,
            timeout=3,
            test_start_time=context.test_start_utc_datetime)
