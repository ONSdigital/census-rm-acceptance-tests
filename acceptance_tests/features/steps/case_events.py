import copy
import functools

from behave import step

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context, \
    store_first_message_in_context
from acceptance_tests.utilities.test_case_helper import tc
from config import Config


@step("messages are emitted to RH and Action Scheduler with {questionnaire_types} questionnaire types")
def gather_messages_emitted_with_qids(context, questionnaire_types):
    context.messages_received = []

    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=len(context.sample_units),
                                                      type_filter='CASE_CREATED'))
    assert len(context.messages_received) == len(context.sample_units)
    context.case_created_events = context.messages_received.copy()
    _test_cases_correct(context)
    context.messages_received = []

    context.expected_uacs_cases = _get_extended_case_created_events_for_uacs(context, questionnaire_types)
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=len(context.expected_uacs_cases),
                                                      type_filter='UAC_UPDATED'))
    assert len(context.messages_received) == len(context.expected_uacs_cases)
    context.uac_created_events = context.messages_received.copy()
    _test_uacs_correct(context)
    context.messages_received = []


@step('UAC Updated events emitted for the {number_of_matching_cases:d} cases with matching treatment codes')
def gather_uac_updated_events(context, number_of_matching_cases):
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=number_of_matching_cases,
                                                      type_filter='UAC_UPDATED'))
    assert len(context.messages_received) == number_of_matching_cases
    context.reminder_uac_updated_events = context.messages_received.copy()
    context.reminder_case_ids = {uac['payload']['uac']['caseId'] for uac in context.reminder_uac_updated_events}
    context.messages_received = []


@step('2 UAC Updated events are emitted for the {number_of_matching_cases:d} cases with matching treatment codes')
def gather_welsh_reminder_uac_events(context, number_of_matching_cases):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=number_of_matching_cases * 2,
                                                      type_filter='UAC_UPDATED'))
    tc.assertEquals(len(context.messages_received), number_of_matching_cases * 2)
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


def _test_cases_correct(context):
    context.expected_sample_units = context.sample_units.copy()

    for msg in context.case_created_events:
        _validate_case(msg)

        for index, sample_unit in enumerate(context.expected_sample_units):
            if _sample_matches_rh_message(sample_unit, msg):
                del context.expected_sample_units[index]
                break
        else:
            tc.fail(msg='Could not find sample unit')


def _sample_matches_rh_message(sample_unit, rh_message):
    return (sample_unit['attributes']['ADDRESS_LINE1'] ==
            rh_message['payload']['collectionCase']['address']['addressLine1']
            and sample_unit['attributes']['ADDRESS_LINE2'] ==
            rh_message['payload']['collectionCase']['address']['addressLine2']
            and sample_unit['attributes']['REGION'][0] == rh_message['payload']['collectionCase']['address']['region'])


def _test_uacs_correct(context):
    assert len(context.messages_received) == len(context.expected_uacs_cases)

    for msg in context.uac_created_events:
        _validate_uac_message(msg)

        for index, case_created_event in enumerate(context.expected_uacs_cases):
            if (_uac_message_matches_rh_message(case_created_event, msg)
                    and (msg['payload']['uac']['questionnaireId'][:2]
                         == case_created_event['expected_questionnaire_type'])):
                del context.expected_uacs_cases[index]
                break
        else:
            assert False, 'Could not find UAC Updated event'


def _validate_uac_message(parsed_body):
    tc.assertEqual(64, len(parsed_body['payload']['uac']['uacHash']))


def _uac_message_matches_rh_message(case_created_event, rh_message):
    return case_created_event['payload']['collectionCase']['id'] == rh_message['payload']['uac']['caseId']


def _validate_case(parsed_body):
    tc.assertEqual('CENSUS', parsed_body['payload']['collectionCase']['survey'])
    tc.assertEqual('ACTIONABLE', parsed_body['payload']['collectionCase']['state'])
    tc.assertEqual(8, len(parsed_body['payload']['collectionCase']['caseRef']))


def get_first_case_created_event(context):
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST,
                                    functools.partial(store_first_message_in_context, context=context,
                                                      type_filter='CASE_CREATED'))
    first_case_created_event = context.first_message
    del context.first_message
    return first_case_created_event


def get_cases_and_uac_event_messages(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=len(context.sample_units),
                                                      type_filter='CASE_CREATED'))
    context.case_created_events = context.messages_received.copy()
    _test_cases_correct(context)
    context.messages_received = []

    context.welsh_cases = [case['payload']['collectionCase'] for case in context.case_created_events
                           if case['payload']['collectionCase']['treatmentCode'].startswith('HH_Q')
                           and case['payload']['collectionCase']['treatmentCode'].endswith('W')]

    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=get_expected_uac_count(context),
                                                      type_filter='UAC_UPDATED'))
    context.uac_created_events = context.messages_received.copy()
    _test_uacs_updated_correct(context)
    context.messages_received = []


def _test_uacs_updated_correct(context):
    case_ids = set(case['payload']['collectionCase']['id'] for case in context.case_created_events)
    tc.assertSetEqual(set(uac['payload']['uac']['caseId'] for uac in context.uac_created_events), case_ids)
    welsh_uac_count = len(tuple(uac_updated_event for uac_updated_event in context.uac_created_events if
                                uac_updated_event['payload']['uac']['questionnaireId'].startswith('03')))
    non_welsh_uac_count = len(context.uac_created_events) - welsh_uac_count
    tc.assertEqual(non_welsh_uac_count, len(context.case_created_events))

    tc.assertEqual(welsh_uac_count, len(context.welsh_cases))


def get_expected_uac_count(context):
    return len(context.welsh_cases) + len(context.case_created_events)
