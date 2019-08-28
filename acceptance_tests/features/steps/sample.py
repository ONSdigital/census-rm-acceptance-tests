import json

from behave import step
from load_sample import load_sample_file

from acceptance_tests.features.steps.case_events import get_cases_and_uac_event_messages
from config import Config


@step('sample file "{sample_file_name}" is loaded')
def load_sample_file_step(context, sample_file_name):
    sample_file_name = f'./resources/sample_files/{sample_file_name}'

    sample_units_raw = load_sample_file(sample_file_name, context.collection_exercise_id, context.action_plan_id,
                                        host=Config.RABBITMQ_HOST, port=Config.RABBITMQ_PORT,
                                        vhost=Config.RABBITMQ_VHOST, exchange=Config.RABBITMQ_EXCHANGE,
                                        user=Config.RABBITMQ_USER, password=Config.RABBITMQ_PASSWORD,
                                        queue_name=Config.RABBITMQ_SAMPLE_INBOUND_QUEUE)

    context.sample_units = [
        json.loads(sample_unit)
        for sample_unit in sample_units_raw.values()
    ]


@step('sample file "{sample_file_name}" is loaded successfully')
def load_sample_file_successfully_step(context, sample_file_name):
    sample_file_name = f'./resources/sample_files/{sample_file_name}'

    sample_units_raw = load_sample_file(sample_file_name, context.collection_exercise_id, context.action_plan_id,
                                        host=Config.RABBITMQ_HOST, port=Config.RABBITMQ_PORT,
                                        vhost=Config.RABBITMQ_VHOST, exchange=Config.RABBITMQ_EXCHANGE,
                                        user=Config.RABBITMQ_USER, password=Config.RABBITMQ_PASSWORD,
                                        queue_name=Config.RABBITMQ_SAMPLE_INBOUND_QUEUE)

    context.sample_units = [
        json.loads(sample_unit)
        for sample_unit in sample_units_raw.values()
    ]

    get_cases_and_uac_event_messages(context)
