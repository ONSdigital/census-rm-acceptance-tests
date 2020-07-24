import csv
import random
from functools import partial
from pathlib import Path
from unittest.mock import patch, Mock

from behave import step
from google.cloud import storage
from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.refusal_processor import RefusalProcessor

from acceptance_tests.utilities.event_helper import get_case_updated_events
from acceptance_tests.utilities.test_case_helper import test_helper

RESOURCE_FILE_PATH = Path(__file__).parents[3].joinpath('resources')


@step('a bulk refusal file is supplied')
def build_bulk_refusal_file(context):
    context.bulk_refusals_file = RESOURCE_FILE_PATH.joinpath('refusal_bulk_test.csv')
    context.bulk_refusals = {}
    for case_created in context.case_created_events:
        context.bulk_refusals[case_created['payload']['collectionCase']['id']] = random.choice(
            ('HARD_REFUSAL',
             'EXTRAORDINARY_REFUSAL')
        )
    with open(context.bulk_refusals_file, 'w') as bulk_refusal_file_write:
        writer = csv.DictWriter(bulk_refusal_file_write, fieldnames=['case_id', 'refusal_type'])
        writer.writeheader()
        for case_id, refusal_type in context.bulk_refusals.items():
            writer.writerow({'case_id': case_id, 'refusal_type': refusal_type})


@step('the bulk refusal file is processed')
def process_bulk_refusal_file(context):
    with patch('toolbox.bulk_processing.bulk_processor.storage') as patch_storage:
        # Patch the bucket interactions so it work purely on local files
        patched_storage_client = patch_storage.Client.return_value
        mock_blob = Mock(spec=storage.Blob)
        mock_blob.name = context.bulk_refusals_file.name
        patched_storage_client.list_blobs.return_value = [mock_blob]
        patched_storage_client.download_blob_to_file.side_effect = partial(
            patch_download_blob_to_file,
            replacement_local_file=context.bulk_refusals_file)
        BulkProcessor(RefusalProcessor()).run()


@step('the cases are marked with the correct refusal')
def check_cases_are_updated_with_correct_refusal_types(context):
    case_updated_events = get_case_updated_events(context, context.bulk_refusals.keys())
    for event in case_updated_events:
        test_helper.assertIn(event['payload']['collectionCase']['id'], context.bulk_refusals.keys(),
                             'Case updated events should only be emitted for refused cases')
        expected_refusal_type = context.bulk_refusals[event['payload']['collectionCase']['id']]
        test_helper.assertEqual(
            event['payload']['collectionCase']['refusalReceived'],
            expected_refusal_type,
            'Refusal type on the case updated events should match the expected type from the bulk file')

    context.bulk_refusals_file.unlink()


def patch_download_blob_to_file(_blob_source, local_destination, replacement_local_file: Path):
    local_destination.write(replacement_local_file.read_bytes())
