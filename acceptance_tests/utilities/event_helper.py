import copy
import functools
import logging
import sys

import luhn
import requests
from retrying import retry
from rfc3339 import parse_datetime
from structlog import wrap_logger

from acceptance_tests.utilities.case_api_helper import get_logged_events_for_case_by_id
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, \
    store_all_case_created_msgs_by_collection_exercise_id, store_all_uac_updated_msgs_by_collection_exercise_id, \
    store_first_message_in_context, store_all_msgs_in_context
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def check_individual_child_case_is_emitted(context, parent_case_id, individual_case_id):
    context.messages_received = []

    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                                    functools.partial(store_all_case_created_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=1,
                                                      collection_exercise_id=context.collection_exercise_id))
    test_helper.assertEqual(len(context.messages_received), 1)
    child_case_uprn = context.messages_received[0]['payload']['collectionCase']['address']['estabUprn']
    parent_case_uprn = _get_parent_case_estab_uprn(parent_case_id)

    test_helper.assertEqual(child_case_uprn, parent_case_uprn, "Parent and child UPRNs must match to link cases")
    context.case_created_events = context.messages_received.copy()
    test_helper.assertEqual(context.case_created_events[0]['payload']['collectionCase']['id'],
                            individual_case_id)


def _get_parent_case_estab_uprn(parent_case_id):
    response = requests.get(f'{Config.CASE_API_CASE_URL}{parent_case_id}')
    return response.json()['estabUprn']


def get_qid_and_uac_from_emitted_child_uac(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(
                                        store_all_uac_updated_msgs_by_collection_exercise_id, context=context,
                                        expected_msg_count=1,
                                        collection_exercise_id=context.collection_exercise_id))

    return context.messages_received[0]['payload']['uac']['uac'], context.messages_received[0]['payload']['uac'][
        'questionnaireId']


def _sample_unit_matches_case_event(sample_unit, case_created_event):
    return (sample_unit['attributes']['ESTAB_UPRN'] ==
            case_created_event['payload']['collectionCase']['address']['estabUprn']
            and sample_unit['attributes']['UPRN'] ==
            case_created_event['payload']['collectionCase']['address']['uprn']
            and sample_unit['attributes']['ADDRESS_LEVEL'] ==
            case_created_event['payload']['collectionCase']['address']['addressLevel'])


def _validate_case(parsed_body):
    test_helper.assertEqual('CENSUS', parsed_body['payload']['collectionCase']['survey'])
    actual_case_ref = parsed_body['payload']['collectionCase']['caseRef']
    test_helper.assertEqual(10, len(actual_case_ref))
    parse_datetime(parsed_body['payload']['collectionCase']['createdDateTime'])
    parse_datetime(parsed_body['payload']['collectionCase']['lastUpdated'])

    test_helper.assertTrue(luhn.verify(actual_case_ref))


def get_and_check_sample_load_case_created_messages(context):
    context.case_created_events = get_case_created_events(context, len(context.sample_units))
    _test_cases_correct(context)
    context.messages_received = []

    context.welsh_cases = [case['payload']['collectionCase'] for case in context.case_created_events
                           if (case['payload']['collectionCase']['treatmentCode'].startswith('HH_Q')
                               or case['payload']['collectionCase']['treatmentCode'].startswith('SPG_Q'))
                           and case['payload']['collectionCase']['treatmentCode'].endswith('W')]


def get_case_created_events(context, expected_number):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                                    functools.partial(store_all_case_created_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=expected_number,
                                                      collection_exercise_id=context.collection_exercise_id))
    return context.messages_received.copy()


def get_and_check_uac_updated_messages(context):
    context.uac_created_events = get_uac_updated_events(context, get_expected_uac_count(context))
    _test_uacs_updated_correct(context)


def get_uac_updated_events(context, expected_number):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(store_all_uac_updated_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=expected_number,
                                                      collection_exercise_id=context.collection_exercise_id))
    uac_updated_events = context.messages_received.copy()
    context.messages_received = []
    return uac_updated_events


def get_last_uac_updated_event(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(store_all_uac_updated_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=1,
                                                      collection_exercise_id=context.collection_exercise_id))
    context.last_uac_updated_event = context.messages_received[0]
    context.messages_received = []


def _test_uacs_updated_correct(context):
    case_ids = set(case['payload']['collectionCase']['id'] for case in context.case_created_events)
    test_helper.assertSetEqual(set(uac['payload']['uac']['caseId'] for uac in context.uac_created_events), case_ids)
    welsh_uac_count = len(tuple(uac_updated_event for uac_updated_event in context.uac_created_events if
                                uac_updated_event['payload']['uac']['questionnaireId'].startswith('03')))
    non_welsh_uac_count = len(context.uac_created_events) - welsh_uac_count
    test_helper.assertEqual(non_welsh_uac_count, len(context.case_created_events))

    test_helper.assertEqual(welsh_uac_count, len(context.welsh_cases))


def _test_cases_correct(context):
    context.expected_sample_units = context.sample_units.copy()
    test_helper.assertEqual(len(context.expected_sample_units), len(context.case_created_events),
                            'Number of cases loaded and case created events do not match')

    for event in context.case_created_events:
        _validate_case(event)

        for index, sample_unit in enumerate(context.expected_sample_units):
            if _sample_unit_matches_case_event(sample_unit, event):
                context.expected_sample_units.pop(index)
                break
        else:
            logger.error('To match case created event to any of the expected sample units',
                         unmatched_sample_units=context.expected_sample_units,
                         case_created_event=event)
            test_helper.fail('Could not find correct case updated messages for all loaded sample units')
            sys.exit(1)  # TODO: remove this exit - it's temporary to diagnose an intermittent test failure in CI


def get_expected_uac_count(context):
    return len(context.welsh_cases) + len(context.case_created_events)


def check_case_created_message_is_emitted(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                                    functools.partial(store_first_message_in_context,
                                                      context=context))
    test_helper.assertEqual(context.first_message['payload']['collectionCase']['id'],
                            context.case_id)
    context.case_created_events = [context.first_message]


def check_survey_launched_case_updated_events(context, case_ids):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                                    functools.partial(store_all_msgs_in_context,
                                                      context=context,
                                                      expected_msg_count=len(case_ids),
                                                      type_filter='CASE_UPDATED'))
    for message in context.messages_received:
        test_helper.assertTrue(message['payload']['collectionCase']['surveyLaunched'],
                               (f'Expected to find {len(case_ids)} CASE_UPDATED events as a result of survey launches '
                                f'found event with "surveyLaunched"=False, cases expected={case_ids}'))
        test_helper.assertIn(message['payload']['collectionCase']['id'], case_ids, 'Found event for unexpected case')


def get_and_test_case_and_uac_msgs_are_correct(context, questionnaire_types):
    get_and_check_sample_load_case_created_messages(context)

    context.expected_uacs_cases = get_extended_case_created_events_for_uacs(context, questionnaire_types)
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(store_all_uac_updated_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=len(context.expected_uacs_cases),
                                                      collection_exercise_id=context.collection_exercise_id))
    test_helper.assertEqual(len(context.messages_received), len(context.expected_uacs_cases))
    context.uac_created_events = context.messages_received.copy()
    test_uacs_correct(context)
    context.messages_received = []


def get_extended_case_created_events_for_uacs(context, questionnaire_types):
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


def test_uacs_correct(context):
    test_helper.assertEqual(len(context.messages_received), len(context.expected_uacs_cases))

    for msg in context.uac_created_events:
        _validate_uac_message(msg)

        for index, case_created_event in enumerate(context.expected_uacs_cases):
            if (uac_message_matches_rh_message(case_created_event, msg)
                    and (msg['payload']['uac']['questionnaireId'][:2]
                         == case_created_event['expected_questionnaire_type'])):
                del context.expected_uacs_cases[index]
                break
        else:
            test_helper.fail('Could not find UAC Updated event')


def _validate_uac_message(parsed_body):
    test_helper.assertEqual(64, len(parsed_body['payload']['uac']['uacHash']))


def test_uacs_correct_for_estab_units(context, expected_uacs, questionnaire_type):
    questionnaire_types_list = questionnaire_type.replace('[', '').replace(']', '').split(',')
    test_helper.assertEqual(len(context.messages_received), expected_uacs)

    for msg in context.uac_created_events:
        _validate_uac_message(msg)
        test_helper.assertIn(msg['payload']['uac']['questionnaireId'][:2], questionnaire_types_list)


def uac_message_matches_rh_message(case_created_event, rh_message):
    return case_created_event['payload']['collectionCase']['id'] == rh_message['payload']['uac']['caseId']


@retry(stop_max_attempt_number=10, wait_fixed=1000)
def check_if_event_list_is_exact_match(event_type_list, case_id):
    actual_logged_events = get_logged_events_for_case_by_id(case_id)
    expected_logged_event_types = event_type_list.replace('[', '').replace(']', '').split(',')
    actual_logged_event_types = [event['eventType'] for event in actual_logged_events]

    test_helper.assertCountEqual(expected_logged_event_types, actual_logged_event_types,
                                 msg="Actual logged event types did not match expected")
