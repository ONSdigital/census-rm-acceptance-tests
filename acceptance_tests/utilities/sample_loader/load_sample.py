import argparse
import csv
import json
import sys
import uuid
from typing import Iterable

from acceptance_tests.utilities.sample_loader.rabbit_context import RabbitContext


def parse_arguments():
    parser = argparse.ArgumentParser(description='Load a sample file into response management.')
    parser.add_argument('sample_file_path', help='path to the sample file', type=str)
    parser.add_argument('collection_exercise_id', help='collection exercise ID', type=str)
    parser.add_argument('action_plan_id', help='action plan ID', type=str)
    parser.add_argument('collection_instrument_id', help='collection instrument ID', type=str)
    return parser.parse_args()


def load_sample_file(sample_file_path, collection_exercise_id, action_plan_id):
    with open(sample_file_path) as sample_file:
        return load_sample(sample_file, collection_exercise_id, action_plan_id)


def load_sample(sample_file: Iterable[str], collection_exercise_id: str, action_plan_id: str):
    sample_file_reader = csv.DictReader(sample_file, delimiter=',')
    return _load_sample_units(action_plan_id, collection_exercise_id, sample_file_reader)


def _load_sample_units(action_plan_id: str, collection_exercise_id: str, sample_file_reader: Iterable[str]):
    sample_units = {}
    with RabbitContext() as rabbit:
        print(f'Loading sample units to queue {rabbit.queue_name}')
        for count, sample_row in enumerate(sample_file_reader):
            sample_unit_id = uuid.uuid4()
            rabbit.publish_message(
                message=_create_case_json(sample=sample_row,
                                          collection_exercise_id=collection_exercise_id,
                                          action_plan_id=action_plan_id),
                content_type='application/json')
            sample_unit = {
                f'sampleunit:{sample_unit_id}': _create_sample_unit_json(sample_unit_id, sample_row)}
            sample_units.update(sample_unit)

            if count % 5000 == 0:
                sys.stdout.write(f'\r{count} sample units loaded')
                sys.stdout.flush()
    print(f'\nAll sample units have been added to the queue {rabbit.queue_name}')
    return sample_units


def _create_sample_unit_json(sample_unit_id, sample_unit) -> str:
    sample_unit = {'id': str(sample_unit_id), 'attributes': sample_unit}
    return json.dumps(sample_unit)


def _create_case_json(sample, collection_exercise_id, action_plan_id) -> str:
    create_case = {'arid': sample['ARID'], 'estabArid': sample['ESTAB_ARID'], 'uprn':  sample['UPRN'],
                   'addressType': sample['ADDRESS_TYPE'], 'estabType': sample['ESTAB_TYPE'],
                   'addressLevel': sample['ADDRESS_LEVEL'], 'abpCode': sample['ABP_CODE'],
                   'organisationName': sample['ORGANISATION_NAME'],
                   'addressLine1': sample['ADDRESS_LINE1'], 'addressLine2': sample['ADDRESS_LINE2'],
                   'addressLine3': sample['ADDRESS_LINE3'], 'townName': sample['TOWN_NAME'],
                   'postcode': sample['POSTCODE'], 'latitude': sample['LATITUDE'],
                   'longitude': sample['LONGITUDE'], 'oa': sample['OA'],
                   'lsoa': sample['LSOA'], 'msoa': sample['MSOA'],
                   'lad': sample['LAD'], 'region': sample['REGION'],
                   'htcWillingness': sample['HTC_WILLINGNESS'], 'htcDigital': sample['HTC_DIGITAL'],
                   'fieldCoordinatorId': sample['FIELDCOORDINATOR_ID'],
                   'fieldOfficerId': sample['FIELDOFFICER_ID'],
                   'treatmentCode': sample['TREATMENT_CODE'],
                   'ceExpectedCapacity': sample['CE_EXPECTED_CAPACITY'],
                   'collectionExerciseId': collection_exercise_id,
                   'actionPlanId': action_plan_id}
    return json.dumps(create_case)


def main():
    args = parse_arguments()
    load_sample_file(args.sample_file_path, args.collection_exercise_id, args.action_plan_id)


if __name__ == "__main__":
    main()
