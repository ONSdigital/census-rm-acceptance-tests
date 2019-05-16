import base64
import json
import uuid
from datetime import datetime

import pika

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
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=Config.RABBITMQ_HOST, port=Config.RABBITMQ_PORT))

    channel = connection.channel()
    channel.queue_purge(queue=Config.RABBITMQ_RH_OUTBOUND_QUEUE)
    channel.queue_purge(queue=Config.RABBITMQ_QUEUE)


def _setup_google_auth():
    if Config.GOOGLE_SERVICE_ACCOUNT_JSON and Config.GOOGLE_APPLICATION_CREDENTIALS:
        sa_json = json.loads(base64.b64decode(Config.GOOGLE_SERVICE_ACCOUNT_JSON))
        with open(Config.GOOGLE_APPLICATION_CREDENTIALS, 'w') as credentials_file:
            json.dump(sa_json, credentials_file)
        print(f'Created GOOGLE_APPLICATION_CREDENTIALS: {Config.GOOGLE_APPLICATION_CREDENTIALS}')
