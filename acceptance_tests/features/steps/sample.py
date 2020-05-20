import json
from pathlib import Path

from behave import step
from load_sample import load_sample_file

from acceptance_tests.utilities.event_helper import get_and_check_case_created_messages, \
    get_and_check_uac_updated_messages
from config import Config


@step('sample file "{sample_file_name}" is loaded')
def load_sample_file_step(context, sample_file_name):
    sample_units_raw = _load_sample(context, sample_file_name)
    context.sample_count = len(sample_units_raw)

    context.sample_units = [
        json.loads(sample_unit)
        for sample_unit in sample_units_raw.values()
    ]


@step('sample file "{sample_file_name}" is loaded successfully')
def load_sample_file_successfully_step(context, sample_file_name):
    sample_units_raw = _load_sample(context, sample_file_name)
    context.sample_count = len(sample_units_raw)

    context.sample_units = [
        json.loads(sample_unit)
        for sample_unit in sample_units_raw.values()
    ]

    get_and_check_case_created_messages(context)
    get_and_check_uac_updated_messages(context)
    context.first_case = context.case_created_events[0]['payload']['collectionCase']


def _load_sample(context, sample_file_name):
    sample_file_path = Path(__file__).parents[3].joinpath('resources', 'sample_files', sample_file_name)
    return load_sample_file(sample_file_path, context.collection_exercise_id, context.action_plan_id,
                            store_loaded_sample_units=True,
                            host=Config.RABBITMQ_HOST, port=Config.RABBITMQ_PORT,
                            vhost=Config.RABBITMQ_VHOST, exchange=Config.RABBITMQ_EXCHANGE,
                            user=Config.RABBITMQ_USER, password=Config.RABBITMQ_PASSWORD,
                            queue_name=Config.RABBITMQ_SAMPLE_INBOUND_QUEUE)
