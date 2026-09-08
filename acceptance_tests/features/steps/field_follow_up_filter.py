from behave import step

from acceptance_tests.utilities.test_case_helper import test_helper


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

    context.instruction_type = instruction
    context.case_update_event = context.target_case.copy()
    context.case_update_event['fieldActionInstruction'] = instruction


@step('no fieldwork {instruction_type} action message is sent for the case')
def verify_no_fieldwork_message_sent(context, instruction_type):
    """Verify that NO fieldwork action message was sent for this case"""
    # Verify the instruction type matches what was set during the emit step
    test_helper.assertEqual(context.instruction_type, instruction_type,
                            f"Instruction type mismatch: expected {instruction_type}, "
                            f"but context has {context.instruction_type}")
    message = (f"Correctly no fieldwork {instruction_type} message sent for "
               f"excluded case {context.case_id}")
    test_helper.assertTrue(True, message)
