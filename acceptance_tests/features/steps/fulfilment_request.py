import functools
import json
import uuid

import requests
from behave import step
from retrying import retry

from acceptance_tests.features.steps.event_log import check_if_event_list_is_exact_match
from acceptance_tests.features.steps.print_file import _check_print_files_have_all_the_expected_data, \
    _check_manifest_files_created
from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_first_message_in_context
from acceptance_tests.utilities.rabbit_helper import store_all_msgs_in_context
from config import Config

notify_stub_url = f'{Config.NOTIFY_STUB_SERVICE}'
get_cases_url = f'{Config.CASEAPI_SERVICE}/cases/'


def get_first_case(context):
    return context.case_created_events[0]['payload']['collectionCase']


@step('an individual questionnaire fulfilment request "{fulfilment_code}" message for a created case is sent')
@step('a PQ continuation fulfilment request event with fulfilment code "{fulfilment_code}" is received by RM')
@step('a PQ fulfilment request event with fulfilment code "{fulfilment_code}" is received by RM')
def send_pq_fulfilment_requested_event(context, fulfilment_code):
    send_print_fulfilment_request(context, fulfilment_code)


def send_print_fulfilment_request(context, fulfilment_code):
    context.first_case = get_first_case(context)

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
                    "fulfilmentCode": fulfilment_code,
                    "caseId": context.first_case['id'],
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


@step('a UAC fulfilment request "{fulfilment_code}" message for a created case is sent')
def create_uac_fulfilment_message(context, fulfilment_code):
    requests.get(f'{notify_stub_url}/reset')

    context.fulfilment_requested_case_id = context.uac_created_events[0]['payload']['uac']['caseId']
    context.individual_case_id = str(uuid.uuid4())
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
                    "fulfilmentCode": fulfilment_code,
                    "caseId": context.fulfilment_requested_case_id,
                    "individualCaseId": context.individual_case_id,
                    "address": {},
                    "contact": {
                        "telNo": "01234567",
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


@step('a print fulfilment request "{fulfilment_code}" message for a created case is sent')
def create_print_fulfilment_message(context, fulfilment_code):
    context.first_case = get_first_case(context)
    context.fulfilment_requested_case_id = context.uac_created_events[0]['payload']['uac']['caseId']
    context.individual_case_id = str(uuid.uuid4())
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
                    "fulfilmentCode": fulfilment_code,
                    "caseId": context.fulfilment_requested_case_id,
                    "individualCaseId": context.individual_case_id,
                    "address": {
                        "addressLine1": "1 main street",
                        "addressLine2": "upper upperingham",
                        "addressLine3": "",
                        "townName": "upton",
                        "postcode": "UP103UP",
                        "region": "E",
                        "latitude": "50.863849",
                        "longitude": "-1.229710",
                        "uprn": "XXXXXXXXXXXXX",
                        "arid": "XXXXX",
                        "addressType": "CE",
                        "estabType": "XXX"
                    },
                    "contact": {
                        "title": "Ms",
                        "forename": "jo",
                        "surname": "smith",
                        "email": "me@example.com",
                        "telNo": "+447890000000"
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


@step("a fulfilment request event is logged")
def check_case_events_logged(context):
    response = requests.get(f'{get_cases_url}{context.fulfilment_requested_case_id}', params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        if case_event['description'] == 'Fulfilment Request Received':
            return
    assert False


@step('notify api was called with template id "{expected_template_id}"')
def check_notify_api_call(context, expected_template_id):
    check_notify_api_called_with_correct_template_id(expected_template_id)


@retry(stop_max_attempt_number=10, wait_fixed=1000)
def check_notify_api_called_with_correct_template_id(expected_template_id):
    response = requests.get(f'{notify_stub_url}/log')
    assert response.status_code == 200, "Unexpected status code"
    response_json = response.json()
    assert len(response_json) == 1, "Incorrect number of responses"
    assert response_json[0]["phone_number"] == '01234567', "Incorrect phone number"
    assert response_json[0]["template_id"] == expected_template_id, "Incorrect template Id"


@step("the continuation fulfilment request event is logged")
@step("the fulfilment request event is logged")
def check_case_events(context):
    response = requests.get(f'{get_cases_url}{context.first_case["id"]}', params={'caseEvents': True})
    assert 200 <= response.status_code <= 299, 'Get cases API call failed'
    cases = response.json()
    assert any(case_event['description'] == 'Fulfilment Request Received' for case_event in cases['caseEvents'])


@step("a new child case is emitted to RH and Action Scheduler")
def child_case_is_emitted(context):
    context.messages_received = []

    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=1,
                                                      type_filter='CASE_CREATED'))
    assert len(context.messages_received) == 1
    child_case_arid = context.messages_received[0]['payload']['collectionCase']['address']['estabArid']
    parent_case_arid = _get_parent_case_estabd_arid(context)

    assert child_case_arid == parent_case_arid, "Parent and child Arids must match to link cases"


def _get_parent_case_estabd_arid(context):
    response = requests.get(f'{get_cases_url}{context.fulfilment_requested_case_id}')
    return response.json()['estabArid']


@step('a supplementary materials fulfilment request event with fulfilment code "{fulfilment_code}" is received by RM')
def send_supplementary_materials_fulfilment_requested_event(context, fulfilment_code):
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST,
                                    functools.partial(store_first_message_in_context, context=context,
                                                      type_filter='CASE_CREATED'))
    context.case_created_events = [context.first_message]
    send_print_fulfilment_request(context, fulfilment_code)


@step("the fulfilment request case has these events logged {expected_event_list}")
def check_fulfilment_events(context, expected_event_list):
    check_if_event_list_is_exact_match(expected_event_list, context.fulfilment_requested_case_id)


@step("the questionnaire fulfilment case has these events logged {expected_event_list}")
def check_questionaire_fulfilment_events(context, expected_event_list):
    check_if_event_list_is_exact_match(expected_event_list, context.first_case['id'])


def create_expected_individual_response_csv(context, fulfilment_code):
    uac = context.uac_created_events[0]['payload']['uac']['uac']
    qid = context.uac_created_events[0]['payload']['uac']['questionnaireId']
    case = context.first_case

    return (
        f'{uac}|'
        f'{qid}'
        f'||||'
        f'Mrs|Test|McTest|'
        f'{case["address"]["addressLine1"]}|'
        f'{case["address"]["addressLine2"]}|'
        f'{case["address"]["addressLine3"]}|'
        f'{case["address"]["townName"]}|'
        f'{case["address"]["postcode"]}|'
        f'{fulfilment_code}'
    )


@step('correctly formatted individual response questionnaires are are created with "{fulfilment_code}"')
def step_impl(context, fulfilment_code):
    expected_csv_lines = [create_expected_individual_response_csv(context, fulfilment_code)]
    _check_print_files_have_all_the_expected_data(context, expected_csv_lines, fulfilment_code)
    _check_manifest_files_created(context, fulfilment_code)


@step("the individual case has these events logged {expected_event_list}")
def check_individual_case_events_logged(context, expected_event_list):
    check_if_event_list_is_exact_match(expected_event_list, context.individual_case_id)
