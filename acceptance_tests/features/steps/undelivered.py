import json
import time

from behave import when
from google.api_core.exceptions import GoogleAPIError
from google.cloud import pubsub_v1

from config import Config


@when("the undelivered PPO message put on GCP pubsub")
def undelivered_ppo_published_to_gcp_pubsub(context):
    context.emitted_case = context.case_created_events[0]['payload']['collectionCase']
    _publish_ppo_undelivered_mail(context, context.emitted_case['caseRef'])
    assert context.sent_to_gcp is True


@when("an undelivered mail QM message is put on GCP pubsub")
def undelivered_qm_published_to_gcp_pubsub(context):
    context.emitted_case = context.case_created_events[0]['payload']['collectionCase']
    questionnaire_id = context.uac_created_events[0]['payload']['uac']['questionnaireId']
    _publish_qm_undelivered_mail(context, questionnaire_id=questionnaire_id)
    assert context.sent_to_gcp is True


def _publish_ppo_undelivered_mail(context, case_ref):
    context.sent_to_gcp = False

    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(Config.PPO_UNDELIVERED_PROJECT_ID, Config.PPO_UNDELIVERED_TOPIC_NAME)

    data = json.dumps({"dateTime": "2019-08-03T14:30:01Z",
                       "caseRef": case_ref,
                       "productCode": "P_OR_H1",
                       "channel": "PPO",
                       "type": "UNDELIVERED_MAIL_REPORTED"})

    future = publisher.publish(topic_path,
                               data=data.encode('utf-8'))

    if not future.done():
        time.sleep(1)
    try:
        future.result(timeout=30)
    except GoogleAPIError:
        return

    print(f'Message published to {topic_path}')

    context.sent_to_gcp = True


def _publish_qm_undelivered_mail(context, tx_id="3d14675d-a25d-4672-a0fe-b960586653e8", questionnaire_id="0"):
    context.sent_to_gcp = False

    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(Config.OFFLINE_RECEIPT_TOPIC_PROJECT, Config.OFFLINE_RECEIPT_TOPIC_ID)

    data = json.dumps({
        "dateTime": "2008-08-24T00:00:00Z",
        "transactionId": tx_id,
        "questionnaireId": questionnaire_id,
        "channel": "PQRS"
    })

    future = publisher.publish(topic_path,
                               data=data.encode('utf-8'))

    if not future.done():
        time.sleep(1)
    try:
        future.result(timeout=30)
    except GoogleAPIError:
        return

    print(f'Message published to {topic_path}')

    context.sent_to_gcp = True
