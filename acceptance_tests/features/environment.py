import base64
import json
import uuid
from datetime import datetime

from acceptance_tests.utilities.rabbit_context import (
    RabbitContext
)
from config import Config


def before_all(context):
    _setup_google_auth()


def before_scenario(context, scenario):
    context.test_start_local_datetime = datetime.now()
    context.collection_exercise_id = str(uuid.uuid4())
    context.action_plan_id = str(uuid.uuid4())
    context.collection_exercise_id = str(uuid.uuid4())
    _purge_queues()


def _purge_queues():
    with RabbitContext() as rabbit:
        rabbit.channel.queue_purge(queue=Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE)
        rabbit.channel.queue_purge(queue=Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE)
        rabbit.channel.queue_purge(queue=Config.RABBITMQ_QUEUE)
        rabbit.channel.queue_purge(queue=Config.RABBITMQ_OUTBOUND_FIELD_QUEUE)


def _setup_google_auth():
    if Config.GOOGLE_SERVICE_ACCOUNT_JSON and Config.GOOGLE_APPLICATION_CREDENTIALS:
        sa_json = json.loads(base64.b64decode(Config.GOOGLE_SERVICE_ACCOUNT_JSON))
        with open(Config.GOOGLE_APPLICATION_CREDENTIALS, 'w') as credentials_file:
            json.dump(sa_json, credentials_file)
        print(f'Created GOOGLE_APPLICATION_CREDENTIALS: {Config.GOOGLE_APPLICATION_CREDENTIALS}')
