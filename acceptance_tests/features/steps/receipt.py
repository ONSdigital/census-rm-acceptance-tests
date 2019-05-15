import json
import time

from behave import when
from coverage.python import os
from google.cloud import pubsub_v1

RECEIPT_TOPIC_PROJECT_ID = "project"
RECEIPT_TOPIC_NAME = "eq-submission-topic"


@when("the a receipt msg for the case is put on the GCP pubsub")
def step_impl(context):
    # how to get the case ID,  I can only imagine that we call the CC Api and look for the correct case?
    publish_to_pubsub("5", "5", "5")


def publish_to_pubsub(tx_id, case_id, questionnaire_id):
    os.environ["PUBSUB_EMULATOR_HOST"] = "localhost:8538"
    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(RECEIPT_TOPIC_PROJECT_ID, RECEIPT_TOPIC_NAME)

    data = json.dumps({
        "timeCreated": "2008-08-24T00:00:00Z",
        "metadata": {
            "case_id": case_id,
            "tx_id": tx_id,
            "questionnaire_id": questionnaire_id,
        }
    })

    future = publisher.publish(topic_path,
                               data=data.encode('utf-8'),
                               eventType='OBJECT_FINALIZE',
                               bucketId='123',
                               objectId=tx_id)
    while not future.done():
        time.sleep(1)

    print(f'Message published to {topic_path}')
