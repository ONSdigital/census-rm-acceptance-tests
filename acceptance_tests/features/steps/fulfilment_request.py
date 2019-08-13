import json
import time

import requests
from behave import step

from acceptance_tests.features.steps.print_file import _check_notification_files_have_all_the_expected_data
from acceptance_tests.utilities.print_file_helper import create_expected_on_request_questionnaire_csv
from acceptance_tests.utilities.rabbit_context import RabbitContext
from config import Config

case_api_url = f'{Config.CASEAPI_SERVICE}/cases/'


@step('a PQ fulfilment request event with fulfilment code "{pack_code}" is received by RM')
def send_fulfilment_requested_event(context, pack_code):
    time.sleep(2)
    context.fulfilment_requested_case_id = context.uac_created_events[0]['payload']['uac']['caseId']

    message = json.dumps(
        {
            "event": {
                "type": "FULFILMENT_REQUESTED",
                "source": "CONTACT_CENTRE_API",
                "channel": "CC",
                "dateTime": "2019-07-07T22:37:11.988+0000",
                "transactionId": "d2541acb-230a-4ade-8123-eee2310c9143"
            },
            "payload": {
                "fulfilmentRequest": {
                    "fulfilmentCode": pack_code,
                    "caseId": context.fulfilment_requested_case_id,
                    "contact": {
                        "title": "Mrs",
                        "forename": "Test",
                        "surname": "McTest"
                    }
                }
            }
        }
    )

    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_FULFILMENT_REQUESTED_ROUTING_KEY)


@step("the fulfilment request event is logged")
def check_case_events(context):
    time.sleep(2)  # Give case processor a chance to process the fulfilment request event
    response = requests.get(f'{case_api_url}{context.fulfilment_requested_case_id}', params={'caseEvents': True})
    response_json = response.json()
    assert any(case_event['description'] == 'Fulfilment Request Received' for case_event in response_json['caseEvents'])


@step('correctly formatted "{pack_code}" on request questionnaire print files are created')
def correct_on_request_questionnaire_print_files(context, pack_code):
    expected_csv_lines = create_expected_on_request_questionnaire_csv(context, pack_code)
    _check_notification_files_have_all_the_expected_data(context, expected_csv_lines, pack_code)
