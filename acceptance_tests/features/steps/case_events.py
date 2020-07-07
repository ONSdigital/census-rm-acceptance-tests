
import functools

from behave import step

from acceptance_tests.utilities.event_helper import get_extended_case_created_events_for_uacs,\
    get_and_test_case_and_uac_msgs_are_correct, test_uacs_correct_for_estab_units
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, \
    store_all_uac_updated_msgs_by_collection_exercise_id, store_first_message_in_context
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step("messages are emitted to RH and Action Scheduler with {questionnaire_types} questionnaire types")
def gather_messages_emitted_with_qids(context, questionnaire_types):
    get_and_test_case_and_uac_msgs_are_correct(context, questionnaire_types)


@step("CE Estab messages are emitted with {questionnaire_types} questionnaire types")
def gather_ce_estab_messages_emitted_with_qids(context, questionnaire_types):
    expected_number_of_uac_messages = 0
    for case in context.case_created_events:
        expected_number_of_uac_messages += case['payload']['collectionCase']['ceExpectedCapacity']
    context.expected_uacs_cases = get_extended_case_created_events_for_uacs(context, questionnaire_types)
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(store_all_uac_updated_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=expected_number_of_uac_messages,
                                                      collection_exercise_id=context.collection_exercise_id))
    test_helper.assertEqual(len(context.messages_received), expected_number_of_uac_messages)
    context.uac_created_events = context.messages_received.copy()
    test_uacs_correct_for_estab_units(context, expected_number_of_uac_messages, questionnaire_types)
    context.messages_received = []


@step('UAC Updated events emitted for the {number_of_matching_cases} cases with matching treatment codes')
def gather_uac_updated_events(context, number_of_matching_cases):
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(store_all_uac_updated_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=int(number_of_matching_cases),
                                                      collection_exercise_id=context.collection_exercise_id))
    test_helper.assertEqual(len(context.messages_received), int(number_of_matching_cases))
    context.reminder_uac_updated_events = context.messages_received.copy()
    context.reminder_case_ids = {uac['payload']['uac']['caseId'] for uac in context.reminder_uac_updated_events}
    context.messages_received = []


@step('2 UAC Updated events are emitted for the {number_of_matching_cases:d} cases with matching treatment codes')
def gather_welsh_reminder_uac_events(context, number_of_matching_cases):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(store_all_uac_updated_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=number_of_matching_cases * 2,
                                                      collection_exercise_id=context.collection_exercise_id))
    test_helper.assertEquals(len(context.messages_received), number_of_matching_cases * 2)
    context.reminder_uac_updated_events = context.messages_received.copy()
    context.reminder_case_ids = {uac['payload']['uac']['caseId'] for uac in context.reminder_uac_updated_events}
    context.messages_received = []


@step('a case_updated msg is emitted where the metadata field "{field}" is "{expected_field_value}"')
def case_updated_msg_with_metadata_field(context, field, expected_field_value):
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                                    functools.partial(store_first_message_in_context,
                                                      context=context))
    test_helper.assertEqual(context.first_message['payload']['metadata'][field], expected_field_value)
