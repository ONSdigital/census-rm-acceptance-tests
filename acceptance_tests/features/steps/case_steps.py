import functools
import json
import logging

from behave import then
from structlog import wrap_logger

from acceptance_tests.controllers.case_controller import get_cases_by_survey_id
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from config import Config

from unittest import TestCase

logger = wrap_logger(logging.getLogger(__name__))

tc = TestCase('__init__')


@then("the sample units are created and stored in the case service")
def check_count_of_cases(context):
    cases = get_cases_by_survey_id(context.survey_id, len(context.sample_units))
    assert len(cases) == len(context.sample_units)


@then("the new cases are emitted to Respondent Home")
def check_messages_are_received(context):
    context.expected_sample_units = context.sample_units.copy()
    context.case_created_events = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_QUEUE, functools.partial(_callback, context=context))

    assert not context.expected_sample_units, 'Some messages are missing'


@then("the QID UAC pairs are emitted to Respondent Home")
def check_uac_messages_are_received(context):
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_QUEUE,
                                    functools.partial(_uac_callback, context=context))

    assert not context.case_created_events, 'Some messages are missing'


def _validate_message(parsed_body):
    tc.assertEqual('CENSUS', parsed_body['payload']['collectionCase']['survey'])
    tc.assertEqual('ACTIONABLE', parsed_body['payload']['collectionCase']['state'])
    tc.assertEqual(8, len(parsed_body['payload']['collectionCase']['caseRef']))


def _validate_uac_message(parsed_body):
    tc.assertEqual(64, len(parsed_body['payload']['uac']['uacHash']))


def _callback(ch, method, _properties, body, context):
    parsed_body = json.loads(body)

    if not parsed_body['event']['type'] == 'CASE_CREATED':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        return

    _validate_message(parsed_body)

    for index, sample_unit in enumerate(context.expected_sample_units):
        if _sample_matches_rh_message(sample_unit, parsed_body):
            context.case_created_events.append(parsed_body)
            del context.expected_sample_units[index]
            ch.basic_ack(delivery_tag=method.delivery_tag)
            break
    else:
        assert False, 'Could not find sample unit'

    if not context.expected_sample_units:
        ch.stop_consuming()


def _uac_callback(ch, method, _properties, body, context):
    parsed_body = json.loads(body)

    if not parsed_body['event']['type'] == 'UAC_UPDATED':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        return

    _validate_uac_message(parsed_body)

    for index, case_created_event in enumerate(context.case_created_events):
        if _uac_message_matches_rh_message(case_created_event, parsed_body):
            del context.case_created_events[index]
            ch.basic_ack(delivery_tag=method.delivery_tag)
            break
    else:
        assert False, 'Could not find UAC Updated event'

    if not context.case_created_events:
        ch.stop_consuming()


def _sample_matches_rh_message(sample_unit, rh_message):
    return sample_unit['attributes']['ADDRESS_LINE1'] == \
           rh_message['payload']['collectionCase']['address']['addressLine1'] \
           and sample_unit['attributes']['ADDRESS_LINE2'] == \
           rh_message['payload']['collectionCase']['address']['addressLine2'] \
           and sample_unit['attributes']['RGN'][0] == rh_message['payload']['collectionCase']['address']['region']


def _assert_equals(expected, actual):
    if expected != actual:
        logger.error(f"Expected {expected}, but got {actual}")
        return False
    return True


def _uac_message_matches_rh_message(case_created_event, rh_message):
    return case_created_event['payload']['collectionCase']['id'] == rh_message['payload']['uac']['caseId']
