import argparse
import csv
import json
import os
import sys
import uuid
from typing import Iterable

import jinja2

from acceptance_tests.utilities.sample_loader.rabbit_context import RabbitContext
from acceptance_tests.utilities.sample_loader.redis_pipeline_context import RedisPipelineContext


def parse_arguments():
    parser = argparse.ArgumentParser(description='Load a sample file into response management.')
    parser.add_argument('sample_file_path', help='path to the sample file', type=str)
    parser.add_argument('collection_exercise_id', help='collection exercise ID', type=str)
    parser.add_argument('action_plan_id', help='action plan ID', type=str)
    parser.add_argument('collection_instrument_id', help='collection instrument ID', type=str)
    return parser.parse_args()


def load_sample_file(sample_file_path, collection_exercise_id, action_plan_id, collection_instrument_id):
    with open(sample_file_path) as sample_file:
        return load_sample(sample_file, collection_exercise_id, action_plan_id, collection_instrument_id)


def load_sample(sample_file: Iterable[str], collection_exercise_id: str, action_plan_id: str,
                collection_instrument_id: str):
    sample_file_reader = csv.DictReader(sample_file, delimiter=',')
    return _load_sample_units(action_plan_id, collection_exercise_id, collection_instrument_id, sample_file_reader)


def _load_sample_units(action_plan_id: str, collection_exercise_id: str, collection_instrument_id: str,
                       sample_file_reader: Iterable[str]):
    sample_units = {}
    case_message_template = jinja2.Environment(
        loader=jinja2.FileSystemLoader([os.path.dirname(__file__)])).get_template('message_template.xml')
    with RabbitContext() as rabbit, RedisPipelineContext() as redis_pipeline:
        print(f'Loading sample units to queue {rabbit.queue_name}')
        for count, sample_row in enumerate(sample_file_reader):
            sample_unit_id = uuid.uuid4()
            rabbit.publish_message(
                message=case_message_template.render(sample=sample_row,
                                                     sample_unit_id=sample_unit_id,
                                                     collection_exercise_id=collection_exercise_id,
                                                     action_plan_id=action_plan_id,
                                                     collection_instrument_id=collection_instrument_id),
                content_type='text/xml')
            sample_unit = {
                f'sampleunit:{sample_unit_id}': _create_sample_unit_json(sample_unit_id, sample_row)}
            redis_pipeline.set_names_to_values(sample_unit)
            sample_units.update(sample_unit)

            if count % 5000 == 0:
                sys.stdout.write(f'\r{count} sample units loaded')
                sys.stdout.flush()
    print(f'\nAll sample units have been added to the queue {rabbit.queue_name} and Redis')
    return sample_units


def _create_sample_unit_json(sample_unit_id, sample_unit) -> str:
    sample_unit = {'id': str(sample_unit_id), 'attributes': sample_unit}
    return json.dumps(sample_unit)


def main():
    args = parse_arguments()
    load_sample_file(args.sample_file_path, args.collection_exercise_id, args.action_plan_id,
                     args.collection_instrument_id)


if __name__ == "__main__":
    main()
