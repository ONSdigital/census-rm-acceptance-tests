import functools

from behave import step

from acceptance_tests.utilities.fieldwork_helper import fieldwork_message_callback
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step('the action instruction messages for only the HH case are emitted to FWMT where the case has a "{filter_column}" '
      'of "{expected_value}"')
@step(
    'the action instruction messages are emitted to FWMT where the case has a "{filter_column}" of "{expected_value}"')
def fwmt_messages_received(context, filter_column, expected_value):
    _check_emitted_action_instructions(context, filter_column, expected_value, 'false')


@step('the action instruction is emitted to FWMT where case has a "{filter_column}" of "{expected_value}" '
      'and CEComplete is "{expected_ce1_complete}"')
def fwmt_message_received_with_ce1_complete(context, filter_column, expected_value, expected_ce1_complete):
    _check_emitted_action_instructions(context, filter_column, expected_value, expected_ce1_complete)


def _check_emitted_action_instructions(context, filter_column, treatment_code, expected_ce1_complete):
    context.expected_cases_for_action = [
        case_created['payload']['collectionCase'] for case_created in context.case_created_events
        if case_created['payload']['collectionCase'][filter_column] == treatment_code
    ]
    context.fieldwork_case_ids = [case['id'] for case in context.expected_cases_for_action]
    context.expected_ce1_complete = expected_ce1_complete

    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE,
                                    functools.partial(fieldwork_message_callback, context=context))

    test_helper.assertFalse(context.expected_cases_for_action,
                            msg="Didn't find all expected fieldwork action instruction messages")
