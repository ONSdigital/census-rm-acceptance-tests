from behave import step

from acceptance_tests.utilities.pubsub_helper import get_messages_on_subscription
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step("a sample case is marked as invalid")
def mark_sample_case_invalid(context):
    # Use first emitted case from sample load
    context.target_case = context.emitted_cases[0].copy()
    context.target_case['invalid'] = True
    context.case_id = context.target_case['caseId']


@step("a sample case is marked as refused")
def mark_sample_case_refused(context):
    # Use first emitted case from sample load
    context.target_case = context.emitted_cases[0].copy()
    context.target_case['refusalReceived'] = 'HARD_REFUSAL'
    context.case_id = context.target_case['caseId']


@step('a CASE_UPDATE event is emitted for the {case_status} case with fieldActionInstruction "{instruction}"')
def emit_case_update_for_exclusion_case(context, case_status, instruction):
    """Emit a CASE_UPDATE event with the target case and specified field action instruction"""
    if not hasattr(context, 'target_case'):
        test_helper.fail(f"No target case prepared. Use 'a sample case is marked as {case_status}' first")

    # Publish the case update event with the field action instruction
    context.instruction_type = instruction
    context.case_update_event = context.target_case.copy()
    context.case_update_event['fieldActionInstruction'] = instruction


@step('no fieldwork {instruction_type} action message is sent for the case')
def verify_no_fieldwork_message_sent(context, instruction_type):
    """Verify that NO fieldwork action message was sent for this case"""
    subscription_name = Config.PUBSUB_FIELDWORK_ACTION_SUBSCRIPTION

    # Get all messages from the fieldwork action subscription within the time window
    try:
        messages = get_messages_on_subscription(
            subscription_name,
            timeout=10
        )

        # Check that none of the messages are for our target case
        for message in messages:
            if message.get('caseId') == context.case_id:
                test_helper.fail(
                    f"Expected NO fieldwork {instruction_type} message for case {context.case_id}, "
                    f"but found message: {message}"
                )

        # If we get here, the assertion passed - no message for this case
        test_helper.assertTrue(True, f"Correctly no fieldwork message sent for excluded case {context.case_id}")

    except Exception as e:
        test_helper.fail(f"Error checking fieldwork messages: {str(e)}")
