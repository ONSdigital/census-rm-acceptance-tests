import time
import uuid
from datetime import datetime

import requests

from acceptance_tests.utilities.rabbit_helper import purge_queues
from config import Config


def after_all(_context):
    purge_queues()


def before_scenario(context, _):
    context.test_start_local_datetime = datetime.now()
    context.collection_exercise_id = str(uuid.uuid4())
    context.action_plan_id = str(uuid.uuid4())
    purge_queues()


def before_tag(_, tag):
    if tag == "clear_for_bad_messages":
        _clear_queues_for_bad_messages_and_reset_exception_manager()


def after_tag(_, tag):
    if tag == "clear_for_bad_messages":
        _clear_queues_for_bad_messages_and_reset_exception_manager()


def _clear_queues_for_bad_messages_and_reset_exception_manager():
    for _ in range(4):
        purge_queues()
        time.sleep(1)
    time.sleep(5)
    requests.get(f'{Config.EXCEPTION_MANAGER_URL}/reset')
