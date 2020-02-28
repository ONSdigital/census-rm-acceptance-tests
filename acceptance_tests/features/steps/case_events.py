import copy
import functools

from behave import step

from acceptance_tests.utilities.event_helper import get_and_check_case_created_messages
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, \
    store_all_uac_updated_msgs_by_collection_exercise_id
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step("messages are emitted to RH and Action Scheduler with {questionnaire_types} questionnaire types")
def gather_messages_emitted_with_qids(context, questionnaire_types):
    get_and_check_case_created_messages(context)

    context.expected_uacs_cases = _get_extended_case_created_events_for_uacs(context, questionnaire_types)
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(store_all_uac_updated_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=len(context.expected_uacs_cases),
                                                      collection_exercise_id=context.collection_exercise_id))
    test_helper.assertEqual(len(context.messages_received), len(context.expected_uacs_cases))
    context.uac_created_events = context.messages_received.copy()
    _test_uacs_correct(context)
    context.messages_received = []


@step('UAC Updated events emitted for the {number_of_matching_cases:d} cases with matching treatment codes')
def gather_uac_updated_events(context, number_of_matching_cases):
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(store_all_uac_updated_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=number_of_matching_cases,
                                                      collection_exercise_id=context.collection_exercise_id))
    test_helper.assertEqual(len(context.messages_received), number_of_matching_cases)
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


def _get_extended_case_created_events_for_uacs(context, questionnaire_types):
    questionnaire_types_list = questionnaire_types.replace('[', '').replace(']', '').split(',')
    expected_uacs_cases = context.case_created_events.copy()

    # 1st pass
    for uac in expected_uacs_cases:
        uac['expected_questionnaire_type'] = questionnaire_types_list[0]

    # If there's 2, current scenario Welsh.  Could be a fancy loop, but not much point
    if len(questionnaire_types_list) == 2:
        second_expected_uacs = copy.deepcopy(context.case_created_events)
        for uac in second_expected_uacs:
            uac['expected_questionnaire_type'] = questionnaire_types_list[1]

        expected_uacs_cases.extend(second_expected_uacs)

    return expected_uacs_cases


def _test_uacs_correct(context):
    test_helper.assertEqual(len(context.messages_received), len(context.expected_uacs_cases))

    for msg in context.uac_created_events:
        _validate_uac_message(msg)

        for index, case_created_event in enumerate(context.expected_uacs_cases):
            if (_uac_message_matches_rh_message(case_created_event, msg)
                    and (msg['payload']['uac']['questionnaireId'][:2]
                         == case_created_event['expected_questionnaire_type'])):
                del context.expected_uacs_cases[index]
                break
        else:
            test_helper.fail('Could not find UAC Updated event')


def _validate_uac_message(parsed_body):
    test_helper.assertEqual(64, len(parsed_body['payload']['uac']['uacHash']))


def _uac_message_matches_rh_message(case_created_event, rh_message):
    return case_created_event['payload']['collectionCase']['id'] == rh_message['payload']['uac']['caseId']
