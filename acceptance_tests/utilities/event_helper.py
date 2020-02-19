import functools
import logging

import requests
from structlog import wrap_logger

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

logger = wrap_logger(logging.getLogger(__name__))
get_cases_url = f'{Config.CASEAPI_SERVICE}/cases/'


def check_individual_child_case_is_emitted(context, parent_case_id, individual_case_id):
    context.messages_received = []

    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=1,
                                                      type_filter='CASE_CREATED'))
    test_helper.assertEqual(len(context.messages_received), 1)
    child_case_arid = context.messages_received[0]['payload']['collectionCase']['address']['estabArid']
    parent_case_arid = _get_parent_case_estab_arid(parent_case_id)

    test_helper.assertEqual(child_case_arid, parent_case_arid, "Parent and child ARIDs must match to link cases")
    context.case_created_events = context.messages_received.copy()
    test_helper.assertEqual(context.case_created_events[0]['payload']['collectionCase']['id'],
                            individual_case_id)


def _get_parent_case_estab_arid(parent_case_id):
    response = requests.get(f'{get_cases_url}{parent_case_id}')
    return response.json()['estabArid']


def get_qid_and_uac_from_emitted_child_uac(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(
                                        store_all_msgs_in_context, context=context,
                                        expected_msg_count=1,
                                        type_filter='UAC_UPDATED'))

    return context.messages_received[0]['payload']['uac']['uac'], context.messages_received[0]['payload']['uac'][
        'questionnaireId']


def _sample_matches_rh_message(sample_unit, rh_message):
    return (sample_unit['attributes']['ADDRESS_LINE1'] ==
            rh_message['payload']['collectionCase']['address']['addressLine1']
            and sample_unit['attributes']['ADDRESS_LINE2'] ==
            rh_message['payload']['collectionCase']['address']['addressLine2']
            and sample_unit['attributes']['REGION'][0] == rh_message['payload']['collectionCase']['address']['region'])


def _validate_case(parsed_body):
    test_helper.assertEqual('CENSUS', parsed_body['payload']['collectionCase']['survey'])
    test_helper.assertEqual(8, len(parsed_body['payload']['collectionCase']['caseRef']))


def get_cases_and_uac_event_messages(context):
    get_and_check_case_created_messages(context)
    get_and_check_uac_updated_messages(context)


def get_and_check_case_created_messages(context):
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


def get_and_check_uac_updated_messages(context):
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=get_expected_uac_count(context),
                                                      type_filter='UAC_UPDATED'))
    context.uac_created_events = context.messages_received.copy()
    _test_uacs_updated_correct(context)
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

    for msg in context.case_created_events:
        _validate_case(msg)

        for index, sample_unit in enumerate(context.expected_sample_units):
            if _sample_matches_rh_message(sample_unit, msg):
                del context.expected_sample_units[index]
                break
        else:
            logger.error('Failed to find all expected sample units',
                         expected_sample_units=context.expected_sample_units,
                         case_created_events=context.case_created_events)
            test_helper.fail('Could not find correct case updated messages for all loaded sample units')


def get_expected_uac_count(context):
    return len(context.welsh_cases) + len(context.case_created_events)
