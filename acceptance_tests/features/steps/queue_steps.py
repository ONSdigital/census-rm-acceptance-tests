import copy
import functools

from behave import step

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context
from acceptance_tests.utilities.test_case_helper import tc
from config import Config


@step("messages are emitted to RH and Action Scheduler with {qid_list_param} qids")
def gather_messages_emitted_with_qids(context, qid_list_param):
    context.messages_received = []

    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=len(context.sample_units),
                                                      type_filter='CASE_CREATED'))
    assert len(context.messages_received) == len(context.sample_units)
    _test_cases_correct(context)
    context.messages_received = []

    context.expected_uacs_cases = _get_extended_case_created_events_for_uacs(context, qid_list_param)
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=len(context.expected_uacs_cases),
                                                      type_filter='UAC_UPDATED'))
    assert len(context.messages_received) == len(context.expected_uacs_cases)
    _test_uacs_correct(context)
    context.messages_received = []


def _get_extended_case_created_events_for_uacs(context, qid_list_param):
    qid_list = qid_list_param.replace('[', '').replace(']', '').split(',')
    expected_uacs_cases = context.case_created_events.copy()

    # 1st pass
    for uac in expected_uacs_cases:
        eu = qid_list[0]
        uac['expected_qid'] = eu

    # If there's 2, current scenario Welsh.  Could be a fancy loop, but not much point
    if len(qid_list) == 2:
        second_uacs = copy.deepcopy(context.case_created_events)
        for uac in second_uacs:
            eu = qid_list[1]
            uac['expected_qid'] = eu

        expected_uacs_cases.extend(second_uacs)

    return expected_uacs_cases


def _test_cases_correct(context):
    context.case_created_events = context.messages_received.copy()
    context.expected_sample_units = context.sample_units.copy()

    for msg in context.case_created_events:
        _validate_case(msg)

        for index, sample_unit in enumerate(context.expected_sample_units):
            if _sample_matches_rh_message(sample_unit, msg):
                del context.expected_sample_units[index]
                break
        else:
            assert False, 'Could not find sample unit'


def _sample_matches_rh_message(sample_unit, rh_message):
    return sample_unit['attributes']['ADDRESS_LINE1'] == \
           rh_message['payload']['collectionCase']['address']['addressLine1'] \
           and sample_unit['attributes']['ADDRESS_LINE2'] == \
           rh_message['payload']['collectionCase']['address']['addressLine2'] \
           and sample_unit['attributes']['REGION'][0] == rh_message['payload']['collectionCase']['address']['region']


def _test_uacs_correct(context):
    assert len(context.messages_received) == len(context.expected_uacs_cases)
    context.uac_created_events = context.messages_received.copy()

    for msg in context.uac_created_events:
        _validate_uac_message(msg)

        for index, case_created_event in enumerate(context.expected_uacs_cases):
            if _uac_message_matches_rh_message(case_created_event, msg) \
                    and msg['payload']['uac']['questionnaireId'][:2] == case_created_event['expected_qid']:
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
