import json
import uuid

import requests
from behave import step

from acceptance_tests.utilities.pubsub_helper import publish_to_pubsub
from config import Config


@step('an individual SMS UAC fulfilment request "{fulfilment_code}" message is sent by EQ')
def send_eq_sms_fulfilment_message(context, fulfilment_code):
    requests.get(f'{Config.NOTIFY_STUB_SERVICE}/reset')

    context.fulfilment_requested_case_id = context.uac_created_events[0]['payload']['uac']['caseId']
    context.individual_case_id = str(uuid.uuid4())
    message = json.dumps(
        {
            "event": {
                "type": "FULFILMENT_REQUESTED",
                "source": "QUESTIONNAIRE_RUNNER",
                "channel": "EQ",
                "dateTime": "2019-07-07T22:37:11.988Z",
                "transactionId": "d2541acb-230a-4ade-8123-eee2310c9143"
            },
            "payload": {
                "fulfilmentRequest": {
                    "fulfilmentCode": fulfilment_code,
                    "caseId": context.fulfilment_requested_case_id,
                    "individualCaseId": context.individual_case_id,
                    "contact": {
                        "telNo": "01234567",
                    }
                }
            }
        }
    )

    publish_to_pubsub(message, Config.EQ_FULFILMENT_PROJECT_ID, Config.EQ_FULFILMENT_TOPIC_NAME)


@step('an individual print UAC fulfilment request "{fulfilment_code}" message is sent by EQ')
def send_eq_print_fulfilment_message(context, fulfilment_code):
    requests.get(f'{Config.NOTIFY_STUB_SERVICE}/reset')

    context.fulfilment_requested_case_id = context.uac_created_events[0]['payload']['uac']['caseId']
    context.individual_case_id = str(uuid.uuid4())
    message = json.dumps(
        {
            "event": {
                "type": "FULFILMENT_REQUESTED",
                "source": "QUESTIONNAIRE_RUNNER",
                "channel": "EQ",
                "dateTime": "2019-07-07T22:37:11.988Z",
                "transactionId": "d2541acb-230a-4ade-8123-eee2310c9143"
            },
            "payload": {
                "fulfilmentRequest": {
                    "fulfilmentCode": fulfilment_code,
                    "caseId": context.fulfilment_requested_case_id,
                    "individualCaseId": context.individual_case_id,
                    "contact": {
                        "title": "Ms",
                        "forename": "jo",
                        "surname": "smith",
                    },
                }
            }
        }
    )

    publish_to_pubsub(message, Config.EQ_FULFILMENT_PROJECT_ID, Config.EQ_FULFILMENT_TOPIC_NAME)
