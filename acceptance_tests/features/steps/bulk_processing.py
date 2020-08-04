import csv
import random
import time
from contextlib import contextmanager
from datetime import datetime
from functools import partial
from pathlib import Path
from unittest.mock import patch, Mock

from behave import step
from google.cloud import storage
from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.invalid_address_processor import InvalidAddressProcessor
from toolbox.bulk_processing.new_address_processor import NewAddressProcessor
from toolbox.bulk_processing.refusal_processor import RefusalProcessor

from acceptance_tests.utilities import database_helper
from acceptance_tests.utilities.event_helper import get_case_updated_events, get_case_created_events
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

RESOURCE_FILE_PATH = Path(__file__).parents[3].joinpath('resources')


@step('a bulk refusal file is supplied')
def build_bulk_refusal_file(context):
    context.bulk_refusals_file = RESOURCE_FILE_PATH.joinpath('bulk_processing_files', 'refusal_bulk_test.csv')
    context.bulk_refusals = {}
    for case_created in context.case_created_events:
        context.bulk_refusals[case_created['payload']['collectionCase']['id']] = random.choice(
            ('HARD_REFUSAL',
             'EXTRAORDINARY_REFUSAL')
        )
    test_helper.assertGreater(len(context.bulk_refusals), 0, 'Must have at least one refusal for this test to be valid')
    with open(context.bulk_refusals_file, 'w') as bulk_refusal_file_write:
        writer = csv.DictWriter(bulk_refusal_file_write, fieldnames=['case_id', 'refusal_type'])
        writer.writeheader()
        for case_id, refusal_type in context.bulk_refusals.items():
            writer.writerow({'case_id': case_id, 'refusal_type': refusal_type})

    if Config.BULK_REFUSAL_BUCKET_NAME:
        # Upload the file to the bucket if we have one
        upload_file_to_bucket(context.bulk_refusals_file,
                              f'refusals_acceptance_tests_{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}.csv',
                              Config.BULK_REFUSAL_BUCKET_NAME)


@step('the bulk refusal file is processed')
def process_bulk_refusal_file(context):
    if Config.BULK_REFUSAL_BUCKET_NAME:
        BulkProcessor(RefusalProcessor()).run()
        return

    # If we don't have a bucket, mock the storage client interactions to work with local files
    with mock_bulk_processor_storage(context.bulk_refusals_file):
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

    if Config.BULK_REFUSAL_BUCKET_NAME:
        clear_bucket(Config.BULK_REFUSAL_BUCKET_NAME)


@step('a bulk new address file "{bulk_new_address_file}" is supplied')
def supply_bulk_new_address_file(context, bulk_new_address_file):
    context.bulk_new_address_file = RESOURCE_FILE_PATH.joinpath('bulk_processing_files', bulk_new_address_file)
    context.bulk_new_addresses = []
    with open(context.bulk_new_address_file, 'r') as bulk_new_address_read:
        reader = csv.DictReader(bulk_new_address_read)
        for row in reader:
            context.bulk_new_addresses.append(row)

    if Config.BULK_NEW_ADDRESS_BUCKET_NAME:
        upload_file_to_bucket(context.bulk_new_address_file,
                              f'new_addresses_acceptance_tests_{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}.csv',
                              Config.BULK_NEW_ADDRESS_BUCKET_NAME)


@step('the bulk new address file is processed')
def process_bulk_new_address_file(context):
    new_address_processor = NewAddressProcessor(action_plan_id=context.action_plan_id,
                                                collection_exercise_id=context.collection_exercise_id)
    if Config.BULK_NEW_ADDRESS_BUCKET_NAME:
        BulkProcessor(new_address_processor).run()
        return

    with mock_bulk_processor_storage(context.bulk_new_address_file):
        BulkProcessor(new_address_processor).run()


@step('CASE_CREATED events are emitted for all the new addressed supplied')
def check_new_cases_are_emitted(context):
    test_helper.assertGreater(len(context.bulk_new_addresses), 0,
                              'Must have at least one new address for this test to be valid')

    context.case_created_events = get_case_created_events(context, len(context.bulk_new_addresses))
    test_helper.assertEqual(len(context.case_created_events), len(context.bulk_new_addresses))

    for address in context.bulk_new_addresses:
        test_helper.assertTrue(any([new_address_matches_case_created(address, case_created_event)
                                    for case_created_event in context.case_created_events]),
                               f'No case created event found for address: {address}')

    if Config.BULK_NEW_ADDRESS_BUCKET_NAME:
        clear_bucket(Config.BULK_NEW_ADDRESS_BUCKET_NAME)


@step('the new address cases are ingested into the database')
def check_new_cases_are_in_action_db(context):
    query = 'SELECT case_id FROM actionv2.cases WHERE action_plan_id = %s AND created_date_time > %s'

    def new_address_load_success_callback(db_result, timeout_deadline):
        if len(db_result) == len(context.bulk_new_addresses):
            new_address_case_ids = {case_created['payload']['collectionCase']['id']
                                    for case_created in context.case_created_events}
            for case_id in (result[0] for result in db_result):
                test_helper.assertIn(case_id, new_address_case_ids,
                                     f'Found case ID {case_id} in action plan {context.action_plan_id} '
                                     f'with no matching created event from the new address bulk load')
            return True
        if time.time() > timeout_deadline:
            test_helper.fail("Didn't find all new address cases in action database before the time out")
        return False

    database_helper.poll_database_query_with_timeout(query, (context.action_plan_id, context.test_start_utc),
                                                     new_address_load_success_callback)


@step('a bulk invalid address file is supplied')
def build_invalid_address_file(context):
    context.bulk_invalid_address_file = RESOURCE_FILE_PATH.joinpath('bulk_processing_files',
                                                                    'invalid_addresses_bulk_test.csv')
    context.bulk_invalid_addresses = {}
    for case_created in context.case_created_events:
        context.bulk_invalid_addresses[case_created['payload']['collectionCase']['id']] = 'TEST_INVALID_REASON'
    test_helper.assertGreater(len(context.bulk_invalid_addresses), 0,
                              'Must have at least one refusal for this test to be valid')
    with open(context.bulk_invalid_address_file, 'w') as bulk_invalid_file_write:
        writer = csv.DictWriter(bulk_invalid_file_write, fieldnames=['case_id', 'reason'])
        writer.writeheader()
        for case_id, reason in context.bulk_invalid_addresses.items():
            writer.writerow({'case_id': case_id, 'reason': reason})

    if Config.BULK_INVALID_ADDRESS_BUCKET_NAME:
        # Upload the file to the bucket if we have one
        upload_file_to_bucket(context.bulk_invalid_address_file,
                              f'invalid_addresses_acceptance_tests_{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}.csv',
                              Config.BULK_INVALID_ADDRESS_BUCKET_NAME)


@step('the bulk invalid address file is processed')
def process_bulk_invalid_address_file(context):
    if Config.BULK_INVALID_ADDRESS_BUCKET_NAME:
        BulkProcessor(InvalidAddressProcessor()).run()
        return

    # If we don't have a bucket, mock the storage client interactions to work with local files
    with mock_bulk_processor_storage(context.bulk_invalid_address_file):
        BulkProcessor(InvalidAddressProcessor()).run()


@step('CASE_UPDATED events are emitted for all the cases in the file with addressInvalid true')
def check_address_invalid_case_updated_events(context):
    address_invalid_case_ids = set(context.bulk_invalid_addresses.keys())
    case_updated_events = get_case_updated_events(context, address_invalid_case_ids)
    test_helper.assertEqual(len(case_updated_events), len(context.bulk_invalid_addresses))
    for event in case_updated_events:
        test_helper.assertTrue(event['payload']['collectionCase']['addressInvalid'],
                               'Address invalid flag must be "True" on all updated events')
        test_helper.assertIn(event['payload']['collectionCase']['id'], address_invalid_case_ids,
                             'Unexpected case ID found on updated event')

    context.bulk_invalid_address_file.unlink()

    if Config.BULK_INVALID_ADDRESS_BUCKET_NAME:
        clear_bucket(Config.BULK_INVALID_ADDRESS_BUCKET_NAME)


def patch_download_blob_to_file(_blob_source, local_destination, replacement_local_file: Path):
    local_destination.write(replacement_local_file.read_bytes())


def new_address_matches_case_created(new_address, case_created_event):
    return all([
        new_address['UPRN'] == case_created_event['payload']['collectionCase']['address']['uprn'],
        new_address['ESTAB_UPRN'] == case_created_event['payload']['collectionCase']['address']['estabUprn'],
        new_address['ADDRESS_LINE1'] == case_created_event['payload']['collectionCase']['address']['addressLine1']
    ])


def clear_bucket(bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs()
    for blob in blobs:
        blob.delete()


def upload_file_to_bucket(file_to_upload: Path, destination_name, bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_name)
    blob.upload_from_filename(str(file_to_upload))


@contextmanager
def mock_bulk_processor_storage(bulk_file: Path):
    # Patch the storage interaction so there is no attempt to use a real bucket
    with patch('toolbox.bulk_processing.bulk_processor.storage') as patch_storage:
        # Patch the bucket interactions so it work purely on local files
        patched_storage_client = patch_storage.Client.return_value
        mock_blob = Mock(spec=storage.Blob)
        mock_blob.name = bulk_file.name
        patched_storage_client.list_blobs.return_value = [mock_blob]
        patched_storage_client.download_blob_to_file.side_effect = partial(
            patch_download_blob_to_file,
            replacement_local_file=bulk_file)

        # Yield here to that anything run in this context will still have the patched bulk processor storage
        yield
