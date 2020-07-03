import json
from pathlib import Path

from config import Config
from load_sample import load_sample_file


def load_sample_file_helper(context, sample_file_name):
    sample_units_raw = _load_sample(context, sample_file_name)
    context.sample_count = len(sample_units_raw)

    context.sample_units = [
        json.loads(sample_unit)
        for sample_unit in sample_units_raw.values()
    ]


def _load_sample(context, sample_file_name):
    sample_file_path = Path(__file__).parents[2].joinpath('resources', 'sample_files', sample_file_name)
    return load_sample_file(sample_file_path, context.collection_exercise_id, context.action_plan_id,
                            store_loaded_sample_units=True,
                            host=Config.RABBITMQ_HOST, port=Config.RABBITMQ_PORT,
                            vhost=Config.RABBITMQ_VHOST, exchange=Config.RABBITMQ_EXCHANGE,
                            user=Config.RABBITMQ_USER, password=Config.RABBITMQ_PASSWORD,
                            queue_name=Config.RABBITMQ_SAMPLE_INBOUND_QUEUE)
