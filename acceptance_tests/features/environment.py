import uuid
from datetime import datetime

import pika

from config import Config


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
