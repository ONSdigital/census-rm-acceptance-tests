import functools
import json
import uuid

import requests
from behave import step
from retrying import retry

from acceptance_tests.utilities.event_helper import check_individual_child_case_is_emitted, \
    get_qid_and_uac_from_emitted_child_uac, check_if_event_list_is_exact_match
from acceptance_tests.utilities.fulfilment_helper import send_print_fulfilment_request, get_first_case
from acceptance_tests.utilities.manifest_file_helper import check_manifest_files_created
from acceptance_tests.utilities.mappings import NOTIFY_TEMPLATE
from acceptance_tests.utilities.print_file_helper import create_expected_individual_response_csv, \
    create_uac_print_materials_csv_line, check_print_files_have_all_the_expected_data
from acceptance_tests.utilities.pubsub_helper import publish_to_pubsub
from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_first_message_in_context
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step('an individual questionnaire fulfilment request "{fulfilment_code}" message for a created case is sent')
@step('a PQ continuation fulfilment request event with fulfilment code "{fulfilment_code}" is received by RM')
@step('a PQ fulfilment request event with fulfilment code "{fulfilment_code}" is received by RM')
def send_pq_fulfilment_requested_event(context, fulfilment_code):
    send_print_fulfilment_request(context, fulfilment_code)


@step('two PQ fulfilment request events with fulfilment code "{fulfilment_code}" are received by RM')
def send_multiple_pd_fulfilment_events(context, fulfilment_code):
    send_multiple_print_fulfilment_requests(context, fulfilment_code)


def send_multiple_print_fulfilment_requests(context, fulfilment_code):
    context.print_cases = [caze['payload']['collectionCase'] for caze in context.case_created_events]
    messages = []
    for caze in context.print_cases:
        messages.append(json.dumps(
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
                        "caseId": caze['id'],
                        "contact": {
                            "title": "Mrs",
                            "forename": "Test",
                            "surname": "McTest"
                        }
                    }
                }
            }
        ))

    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        for message in messages:
            rabbit.publish_message(
                message=message,
                content_type='application/json',
                routing_key=Config.RABBITMQ_FULFILMENT_REQUESTED_ROUTING_KEY)


@step('a UAC fulfilment request "{fulfilment_code}" message for a created case is sent')
def create_uac_fulfilment_message(context, fulfilment_code):
    requests.get(f'{Config.NOTIFY_STUB_SERVICE}/reset')

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


@step('a HH print UAC fulfilment request "{fulfilment_code}" message for a created case is sent')
def create_HH_uac_fulfilment_message(context, fulfilment_code):
    context.fulfilment_requested_case_id = context.uac_created_events[0]['payload']['uac']['caseId']
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
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


@step('an individual print fulfilment request "{fulfilment_code}" is received by RM')
def create_individual_print_fulfilment_message(context, fulfilment_code):
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


@step('an individual UAC SMS fulfilment request "{fulfilment_code}" is received by RM')
def create_individual_uac_sms_fulfilment_message_without_ind_case_id(context, fulfilment_code):
    requests.get(f'{Config.NOTIFY_STUB_SERVICE}/reset')

    context.first_case = get_first_case(context)
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
                    "fulfilmentCode": fulfilment_code,
                    "caseId": context.fulfilment_requested_case_id,
                    "individualCaseId": None,
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
                        "addressType": "CE",
                        "estabType": "XXX"
                    },
                    "contact": {
                        "title": "Ms",
                        "forename": "jo",
                        "surname": "smith",
                        "email": "me@example.com",
                        "telNo": "01234567"
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
    response = requests.get(f"{Config.CASE_API_CASE_URL}{context.fulfilment_requested_case_id}",
                            params={'caseEvents': True})
    response_json = response.json()
    for case_event in response_json['caseEvents']:
        if case_event['description'] == 'Fulfilment Request Received':
            return
    test_helper.fail('Did not find fulfilment request event')


@step('notify api was called with SMS template "{expected_template}"')
def check_notify_api_call(context, expected_template: str):
    _check_notify_api_called_with_correct_template_id(NOTIFY_TEMPLATE['_'.join(expected_template.lower().split())])


@retry(stop_max_attempt_number=10, wait_fixed=1000)
def _check_notify_api_called_with_correct_template_id(expected_template_id):
    response = requests.get(f'{Config.NOTIFY_STUB_SERVICE}/log')
    test_helper.assertEqual(response.status_code, 200, "Unexpected status code")
    response_json = response.json()
    test_helper.assertEqual(len(response_json), 1, "Incorrect number of responses")
    test_helper.assertEqual(response_json[0]["phone_number"], '01234567', "Incorrect phone number")
    test_helper.assertEqual(response_json[0]["template_id"], expected_template_id, "Incorrect template Id")


@step("the continuation fulfilment request event is logged")
@step("the fulfilment request event is logged")
def check_case_events(context):
    response = requests.get(f'{Config.CASE_API_CASE_URL}{context.first_case["id"]}', params={'caseEvents': True})
    test_helper.assertTrue(200 <= response.status_code <= 299, 'Get cases API call failed')
    cases = response.json()
    test_helper.assertTrue(any(case_event['description'] == 'Fulfilment Request Received'
                               for case_event in cases['caseEvents']))


@step("a new individual child case for the fulfilment is emitted to RH and Action Scheduler")
def fulfilment_child_case_is_emitted(context):
    check_individual_child_case_is_emitted(context, context.fulfilment_requested_case_id,
                                           context.individual_case_id)


@step('a supplementary materials fulfilment request event with fulfilment code "{fulfilment_code}" is received by RM')
def send_supplementary_materials_fulfilment_requested_event(context, fulfilment_code):
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                                    functools.partial(store_first_message_in_context, context=context,
                                                      type_filter='CASE_CREATED'))
    context.case_created_events = [context.first_message]
    send_print_fulfilment_request(context, fulfilment_code)


@step("the fulfilment request case has these events logged {expected_event_list}")
def check_fulfilment_events(context, expected_event_list):
    check_if_event_list_is_exact_match(expected_event_list, context.fulfilment_requested_case_id)


@step("an individual case has been created and only has logged events of {expected_event_list}")
def check_individual_fulfilment_events(context, expected_event_list):
    check_if_event_list_is_exact_match(expected_event_list, context.individual_case_id)


@step("the questionnaire fulfilment case has these events logged {expected_event_list}")
def check_questionnaire_fulfilment_events(context, expected_event_list):
    check_if_event_list_is_exact_match(expected_event_list, context.first_case['id'])


@step("the multiple questionnaire fulfilment cases have these events logged {expected_event_list}")
def check_multiple_questionnaire_fulfilment_events(context, expected_event_list):
    for caze in context.print_cases:
        check_if_event_list_is_exact_match(expected_event_list, caze['id'])


@step(
    'correctly formatted individual response questionnaires are created for "{fulfilment_code}" '
    'with questionnaire type "{questionnaire_type}"')
def check_individual_questionnaire_print_requests(context, fulfilment_code, questionnaire_type):
    individual_case = requests.get(f'{Config.CASE_API_CASE_URL}{context.individual_case_id}').json()
    uac, qid = get_qid_and_uac_from_emitted_child_uac(context)
    test_helper.assertEqual(qid[:2], questionnaire_type, "Incorrect questionnaire type")
    expected_csv_lines = [create_expected_individual_response_csv(individual_case, uac, qid, fulfilment_code)]

    check_print_files_have_all_the_expected_data(context, expected_csv_lines, fulfilment_code)
    check_manifest_files_created(context, fulfilment_code)


@step(
    'correctly formatted individual UAC print responses are created for "{fulfilment_code}" '
    'with questionnaire type "{questionnaire_type}"')
def check_individual_uac_print_requests(context, fulfilment_code, questionnaire_type):
    individual_case = requests.get(f'{Config.CASE_API_CASE_URL}{context.individual_case_id}').json()
    uac, qid = get_qid_and_uac_from_emitted_child_uac(context)
    test_helper.assertEqual(qid[:2], questionnaire_type, "Incorrect questionnaire type")
    expected_csv_lines = [create_uac_print_materials_csv_line(individual_case, uac, qid, fulfilment_code)]

    check_print_files_have_all_the_expected_data(context, expected_csv_lines, fulfilment_code)
    check_manifest_files_created(context, fulfilment_code)


@step("the individual case has these events logged {expected_event_list}")
def check_individual_case_events_logged(context, expected_event_list):
    check_if_event_list_is_exact_match(expected_event_list, context.individual_case_id)


@step("QM sends a fulfilment confirmed message via pubsub")
def qm_sends_fulfilment_confirmed(context):
    context.first_case = get_first_case(context)
    uac_created_message = context.uac_created_events[0]

    data = json.dumps({"transactionId": str(uuid.uuid4()),
                       "dateTime": "2019-08-03T14:30:01",
                       "questionnaireId": uac_created_message['payload']['uac']['questionnaireId'],
                       "productCode": "P_OR_H1",
                       "channel": "QM",
                       "type": "FULFILMENT_CONFIRMED"})

    publish_to_pubsub(data, Config.FULFILMENT_CONFIRMED_PROJECT_ID, Config.FULFILMENT_CONFIRMED_TOPIC_ID)


@step("PPO sends a fulfilment confirmed message via pubsub")
def ppo_sends_fulfilment_confirmed(context):
    context.first_case = get_first_case(context)

    data = json.dumps({"transactionId": str(uuid.uuid4()),
                       "dateTime": "2019-08-03T14:30:01",
                       "caseRef": context.first_case['caseRef'],
                       "productCode": "P_OR_H1",
                       "channel": "PPO",
                       "type": "FULFILMENT_CONFIRMED"})

    publish_to_pubsub(data, Config.FULFILMENT_CONFIRMED_PROJECT_ID, Config.FULFILMENT_CONFIRMED_TOPIC_ID)
