import functools
import json
import logging

import pika
from behave import then
from structlog import wrap_logger

from acceptance_tests.controllers.case_controller import get_cases_by_survey_id
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
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=Config.RABBITMQ_HOST, port=Config.RABBITMQ_PORT))

    channel = connection.channel()

    connection.add_timeout(deadline=30, callback_method=functools.partial(_timeout_callback, channel))

    expected_sample_units = context.sample_units.copy()
    channel.basic_consume(queue=Config.RABBITMQ_RH_OUTBOUND_QUEUE,
                          consumer_callback=functools.partial(_callback, expected_sample_units=expected_sample_units))

    channel.start_consuming()

    assert not expected_sample_units, 'Some messages are missing'


def _timeout_callback(ch):
    logger.error('Timed out waiting for messages')
    ch.stop_consuming()


def _validate_message(parsed_body):
    tc.assertEqual('CENSUS', parsed_body['payload']['collectionCase']['survey'])
    tc.assertEqual('ACTIONABLE', parsed_body['payload']['collectionCase']['state'])
    tc.assertEqual(8, len(parsed_body['payload']['collectionCase']['caseRef']))


def _callback(ch, method, properties, body, expected_sample_units):
    ch.basic_ack(delivery_tag=method.delivery_tag)

    parsed_body = json.loads(body)

    _validate_message(parsed_body)

    for index, sample_unit in enumerate(expected_sample_units):
        if _sample_matches_rh_message(sample_unit, parsed_body):
            del expected_sample_units[index]
            break
    else:
        assert False, 'Could not find sample unit'

    if not expected_sample_units:
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
