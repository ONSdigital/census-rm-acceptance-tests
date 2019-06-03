import base64
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from acceptance_tests.utilities.rabbit_context import (
    RabbitContext
)
from config import Config


def before_all(_context):
    _setup_google_auth()


def before_scenario(context, _scenario):
    context.test_start_local_datetime = datetime.now()
    context.collection_exercise_id = str(uuid.uuid4())
    context.action_plan_id = str(uuid.uuid4())
    context.collection_exercise_id = str(uuid.uuid4())
    _purge_queues()
    _create_and_clean_up_test_files(context)


def after_scenario(context, _scenario):
    _remove_test_files(context)


def _remove_test_files(context):
    shutil.rmtree(context.test_file_path)


def _purge_queues():
    with RabbitContext() as rabbit:
        rabbit.channel.queue_purge(queue=Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE)
        rabbit.channel.queue_purge(queue=Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE)
        rabbit.channel.queue_purge(queue=Config.RABBITMQ_QUEUE)
        rabbit.channel.queue_purge(queue=Config.RABBITMQ_UNADDRESSED_REQUEST_QUEUE)


def _setup_google_auth():
    if Config.GOOGLE_SERVICE_ACCOUNT_JSON and Config.GOOGLE_APPLICATION_CREDENTIALS:
        sa_json = json.loads(base64.b64decode(Config.GOOGLE_SERVICE_ACCOUNT_JSON))
        with open(Config.GOOGLE_APPLICATION_CREDENTIALS, 'w') as credentials_file:
            json.dump(sa_json, credentials_file)
        print(f'Created GOOGLE_APPLICATION_CREDENTIALS: {Config.GOOGLE_APPLICATION_CREDENTIALS}')


def _create_and_clean_up_test_files(context):
    context.test_file_path = Path(__file__).parent.parent.resolve().joinpath('tmp_test_files')
    if context.test_file_path.exists():
        shutil.rmtree(context.test_file_path)
    context.test_file_path.mkdir()
