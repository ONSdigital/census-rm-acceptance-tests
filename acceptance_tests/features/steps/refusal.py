import functools
import json
import xml.etree.ElementTree as ET

import requests
from behave import then

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from config import Config

caseapi_url = f'{Config.CASEAPI_SERVICE}/cases/'


@then("a refusal message for a created case is received")
def create_refusal(context):
    context.refused_case_id = context.uac_created_events[0]['payload']['uac']['caseId']
    context.refused_questionnaire_id = context.uac_created_events[0]['payload']['uac']['questionnaireId']

    message = json.dumps(
        {
            "event": {
                "type": "REFUSAL_RECEIVED",
                "source": "CONTACT_CENTRE_API",
                "channel": "CC",
                "dateTime": "2019-07-07T22:37:11.988+0000",
                "transactionId": "a6f9f129-f582-4011-8b48-d787c45cab26"
            },
            "payload": {
                "refusal": {
                    "questionnaireId": context.refused_questionnaire_id,
                    "type": "HARD_REFUSAL",
                    "report": "Test refusal",
                    "agentId": None,
                    "collectionCase": {
                        "id": context.refused_case_id
                    },
                    "contact": {
                        "title": "Mr",
                        "forename": "Test",
                        "surname": "Testing",
                        "email": None,
                        "telNo": "01234123123"
                    },
                    "address": {
                        "addressLine1": "123",
                        "addressLine2": "Fake Street",
                        "addressLine3": "",
                        "townName": "Test Town",
                        "postcode": "XX1 XX1",
                        "region": "W"
                    }
                }
            }
        }
    )

    with RabbitContext(queue_name=Config.RABBITMQ_INBOUND_REFUSAL_QUEUE) as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json')


@then("the case is marked as refused")
def check_case_events(context):
    response = requests.get(f'{caseapi_url}{context.refused_case_id}', params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        if case_event['description'] == 'Refusal Received':
            return
    assert False


@then("the case is excluded from FWMT action rule")
def check_case_excluded_from_action_rule(context):
    context.expected_sample_units = [
        sample_unit
        for sample_unit in context.sample_units.copy() if sample_unit['attributes']['TREATMENT_CODE'] == 'HH_QF2R1E'
    ]

    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE_TEST,
                                    functools.partial(_callback, context=context))

    assert not context.expected_sample_units, 'Some messages are missing'


def _callback(ch, method, _properties, body, context):
    root = ET.fromstring(body)

    if not root[0].tag == 'actionRequest':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        assert False, 'Unexpected message on Action.Field case queue'

    for sample_unit in context.expected_sample_units:
        if sample_unit['id'] == root.find('.//caseId').text:
            assert False, f"Unexpected caseId {sample_unit['id']} found in Action.Field message"
