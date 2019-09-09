import functools
import json
import time
import uuid
import xml.etree.ElementTree as ET

from behave import when, step
from google.api_core.exceptions import GoogleAPIError
from google.cloud import pubsub_v1

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from config import Config


@when("an undelivered mail QM message is put on GCP pubsub")
def undelivered_qm_published_to_gcp_pubsub(context):
    context.emitted_case = context.case_created_events[0]['payload']['collectionCase']
    questionnaire_id = context.uac_created_events[0]['payload']['uac']['questionnaireId']
    _publish_qm_undelivered_mail(context, questionnaire_id=questionnaire_id)
    assert context.sent_to_gcp is True


@when("an undelivered mail PPO message is put on GCP pubsub")
def undelivered_ppo_published_to_gcp_pubsub(context):
    context.emitted_case = context.case_created_events[0]['payload']['collectionCase']
    case_ref = context.emitted_case['caseRef']
    _publish_ppo_undelivered_mail(context, case_ref=case_ref)
    assert context.sent_to_gcp is True


@step("an ActionRequest event is sent to field work management")
def action_request_event_sent_to_fwm(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE_TEST, functools.partial(
        _field_work_receipt_callback, context=context))

    assert context.fwmt_emitted_case_id == context.emitted_case["id"]
    assert context.addressType == 'HH'
    assert context.fwmt_emitted_undelivered_flag == 'true'


def _field_work_receipt_callback(ch, method, _properties, body, context):
    root = ET.fromstring(body)

    if not root[0].tag == 'actionRequest':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        assert False, 'Unexpected message on Action.Field case queue, wanted actionRequest'

    context.addressType = root[0].find('.//addressType').text
    context.fwmt_emitted_case_id = root[0].find('.//caseId').text
    context.fwmt_emitted_undelivered_flag = root[0].find('.//undeliveredAsAddress').text
    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()


def _publish_ppo_undelivered_mail(context, case_ref):
    context.sent_to_gcp = False

    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(Config.PPO_UNDELIVERED_PROJECT_ID, Config.PPO_UNDELIVERED_TOPIC_NAME)

    data = json.dumps({"transactionId": str(uuid.uuid4()),
                       "dateTime": "2019-08-03T14:30:01",
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


def _publish_qm_undelivered_mail(context, questionnaire_id):
    context.sent_to_gcp = False

    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(Config.QM_UNDELIVERED_PROJECT_ID, Config.QM_UNDELIVERED_TOPIC_NAME)

    data = json.dumps({
        "transactionId": str(uuid.uuid4()),
        "dateTime": "2008-08-24T00:00:00",
        "questionnaireId": questionnaire_id
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
