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
from toolbox.bulk_processing.address_update_processor import AddressUpdateProcessor
from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.deactivate_uac_processor import DeactivateUacProcessor
from toolbox.bulk_processing.invalid_address_processor import InvalidAddressProcessor
from toolbox.bulk_processing.new_address_processor import NewAddressProcessor
from toolbox.bulk_processing.refusal_processor import RefusalProcessor

from acceptance_tests import RESOURCE_FILE_PATH
from acceptance_tests.utilities import database_helper
from acceptance_tests.utilities.case_api_helper import get_logged_events_for_case_by_id, \
    get_case_and_case_events_by_case_id
from acceptance_tests.utilities.event_helper import get_case_updated_events, get_case_created_events, \
    get_uac_updated_events
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step('a bulk refusal file is supplied')
def build_bulk_refusal_file(context):
    # Build a bulk refusal file with a row for each the stored case created event
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

    # Upload the file to a real bucket if one is configured
    if Config.BULK_REFUSAL_BUCKET_NAME:
        clear_bucket(Config.BULK_REFUSAL_BUCKET_NAME)
        upload_file_to_bucket(context.bulk_refusals_file,
                              f'refusals_acceptance_tests_{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}.csv',
                              Config.BULK_REFUSAL_BUCKET_NAME)


@step('the bulk refusal file is processed')
def process_bulk_refusal_file(context):
    # Run against the real bucket if it is configured
    if Config.BULK_REFUSAL_BUCKET_NAME:
        BulkProcessor(RefusalProcessor()).run()
        return

    # If we don't have a bucket, mock the storage bucket client interactions to work with only local files
    with mock_bulk_processor_bucket(context.bulk_refusals_file):
        BulkProcessor(RefusalProcessor()).run()


@step('the cases are marked with the correct refusal')
def check_cases_are_updated_with_correct_refusal_types(context):
    case_updated_events = get_case_updated_events(context, len(context.bulk_refusals))
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

    # Upload the file to a real bucket if one is configured
    if Config.BULK_NEW_ADDRESS_BUCKET_NAME:
        clear_bucket(Config.BULK_NEW_ADDRESS_BUCKET_NAME)
        upload_file_to_bucket(context.bulk_new_address_file,
                              f'new_addresses_acceptance_tests_{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}.csv',
                              Config.BULK_NEW_ADDRESS_BUCKET_NAME)


@step('the bulk new address file is processed')
def process_bulk_new_address_file(context):
    new_address_processor = NewAddressProcessor(action_plan_id=context.action_plan_id,
                                                collection_exercise_id=context.collection_exercise_id)

    # Run against the real bucket if it is configured
    if Config.BULK_NEW_ADDRESS_BUCKET_NAME:
        BulkProcessor(new_address_processor).run()
        return

    # If we don't have a bucket, mock the storage bucket client interactions to work with only local files
    with mock_bulk_processor_bucket(context.bulk_new_address_file):
        BulkProcessor(new_address_processor).run()


@step('CASE_CREATED events are emitted for all the new addressed supplied')
def check_new_cases_are_emitted(context):
    test_helper.assertGreater(len(context.bulk_new_addresses), 0,
                              'Must have at least one new address for this test to be valid')

    context.case_created_events = get_case_created_events(context, len(context.bulk_new_addresses))
    test_helper.assertEqual(len(context.case_created_events), len(context.bulk_new_addresses),
                            'Number of created cases should match number supplied in the bulk file')

    for address in context.bulk_new_addresses:
        test_helper.assertTrue(any([new_address_matches_case_created(address, case_created_event)
                                    for case_created_event in context.case_created_events]),
                               f'No case created event found for address: {address}')

    if Config.BULK_NEW_ADDRESS_BUCKET_NAME:
        clear_bucket(Config.BULK_NEW_ADDRESS_BUCKET_NAME)


@step('the new address cases are ingested into the database')
def check_new_cases_are_in_action_db(context):
    case_ids_query = 'SELECT case_id FROM actionv2.cases WHERE action_plan_id = %s AND created_date_time > %s'

    def new_address_load_success_callback(db_result, timeout_deadline):
        # Check we have the right number of cases and all the expected case ID's are present
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

    database_helper.poll_action_database_with_timeout(query=case_ids_query,
                                                      query_vars=(context.action_plan_id, context.test_start_utc),
                                                      result_success_callback=new_address_load_success_callback)


@step('a bulk invalid address file is supplied')
def build_invalid_address_file(context):
    # Build a bulk invalid address file with a row for each the stored case created event
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

    # Upload the file to a real bucket if one is configured
    if Config.BULK_INVALID_ADDRESS_BUCKET_NAME:
        clear_bucket(Config.BULK_INVALID_ADDRESS_BUCKET_NAME)
        upload_file_to_bucket(context.bulk_invalid_address_file,
                              f'invalid_addresses_acceptance_tests_{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}.csv',
                              Config.BULK_INVALID_ADDRESS_BUCKET_NAME)


@step('the bulk invalid address file is processed')
def process_bulk_invalid_address_file(context):
    # Run against the real bucket if it is configured
    if Config.BULK_INVALID_ADDRESS_BUCKET_NAME:
        BulkProcessor(InvalidAddressProcessor()).run()
        return

    # If we don't have a bucket, mock the storage bucket client interactions to work with only local files
    with mock_bulk_processor_bucket(context.bulk_invalid_address_file):
        BulkProcessor(InvalidAddressProcessor()).run()


@step('CASE_UPDATED events are emitted for all the cases in the file with addressInvalid true')
def check_address_invalid_case_updated_events(context):
    address_invalid_case_ids = set(context.bulk_invalid_addresses.keys())
    case_updated_events = get_case_updated_events(context, len(address_invalid_case_ids))
    test_helper.assertEqual(len(case_updated_events), len(context.bulk_invalid_addresses))
    for event in case_updated_events:
        test_helper.assertTrue(event['payload']['collectionCase']['addressInvalid'],
                               'Address invalid flag must be "True" on all updated events')
        test_helper.assertIn(event['payload']['collectionCase']['id'], address_invalid_case_ids,
                             'Unexpected case ID found on updated event')

    context.bulk_invalid_address_file.unlink()
    if Config.BULK_INVALID_ADDRESS_BUCKET_NAME:
        clear_bucket(Config.BULK_INVALID_ADDRESS_BUCKET_NAME)


@step('a bulk address update file is supplied')
def build_address_updates_file(context):
    # Build a bulk invalid address file with a row for each the stored case created event
    context.bulk_address_updates_file = RESOURCE_FILE_PATH.joinpath('bulk_processing_files',
                                                                    'address_updates_bulk_test.csv')
    context.bulk_address_updates = []
    for case_created in context.case_created_events:
        context.bulk_address_updates.append({
            'CASE_ID': case_created['payload']['collectionCase']['id'],
            'UPRN': '123456789',
            'ESTAB_UPRN': '987654321',
            'ESTAB_TYPE': 'ROYAL HOUSEHOLD',
            'ABP_CODE': '4321',
            'ORGANISATION_NAME': 'foo_incorporated',
            'ADDRESS_LINE1': 'foo flat1',
            'ADDRESS_LINE2': 'foo some road',
            'ADDRESS_LINE3': 'foo somewhere',
            'TOWN_NAME': 'foo some town',
            'POSTCODE': 'F00 BAR',
            'LATITUDE': '0.0',
            'LONGITUDE': '127.0',
            'OA': 'foo_1',
            'LSOA': 'foo_2',
            'MSOA': 'foo_3',
            'LAD': 'foo_4',
            'HTC_WILLINGNESS': '5',
            'HTC_DIGITAL': '3',
            'TREATMENT_CODE': 'HH_LP1E',
            'FIELDCOORDINATOR_ID': 'ABC123',
            'FIELDOFFICER_ID': 'XYZ999',
            'CE_EXPECTED_CAPACITY': '10',
            'CE_SECURE': '1',
            'PRINT_BATCH': '99',
        })
    test_helper.assertGreater(len(context.bulk_address_updates), 0,
                              'Must have at least one update for this test to be valid')
    with open(context.bulk_address_updates_file, 'w') as bulk_updates_file_write:
        writer = csv.DictWriter(bulk_updates_file_write, fieldnames=list(context.bulk_address_updates[0].keys()))
        writer.writeheader()
        for row in context.bulk_address_updates:
            writer.writerow(row)

    # Upload the file to a real bucket if one is configured
    if Config.BULK_ADDRESS_UPDATE_BUCKET_NAME:
        clear_bucket(Config.BULK_INVALID_ADDRESS_BUCKET_NAME)
        upload_file_to_bucket(context.bulk_address_updates_file,
                              f'address_updates_acceptance_tests_{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}.csv',
                              Config.BULK_ADDRESS_UPDATE_BUCKET_NAME)


@step('the bulk address update file is processed')
def process_bulk_address_updates_file(context):
    # Run against the real bucket if it is configured
    if Config.BULK_ADDRESS_UPDATE_BUCKET_NAME:
        BulkProcessor(AddressUpdateProcessor()).run()
        return

    # If we don't have a bucket, mock the storage bucket client interactions to work with only local files
    with mock_bulk_processor_bucket(context.bulk_address_updates_file):
        BulkProcessor(AddressUpdateProcessor()).run()


@step('CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false')
def check_address_update_case_updated_events(context):
    address_update_case_ids = set(row['CASE_ID'] for row in context.bulk_address_updates)
    context.case_updated_events = get_case_updated_events(context, len(address_update_case_ids))
    test_helper.assertEqual(len(context.case_updated_events), len(context.bulk_address_updates))
    for event in context.case_updated_events:
        collection_case = event['payload']['collectionCase']
        test_helper.assertIn(collection_case['id'], address_update_case_ids,
                             'Unexpected case ID found on updated event')
        test_helper.assertEqual(collection_case['treatmentCode'], context.bulk_address_updates[0]['TREATMENT_CODE'])
        test_helper.assertEqual(collection_case['address']['estabType'], context.bulk_address_updates[0]['ESTAB_TYPE'])
        test_helper.assertEqual(collection_case['oa'], context.bulk_address_updates[0]['OA'])
        test_helper.assertEqual(collection_case['lsoa'], context.bulk_address_updates[0]['LSOA'])
        test_helper.assertEqual(collection_case['msoa'], context.bulk_address_updates[0]['MSOA'])
        test_helper.assertEqual(collection_case['lad'], context.bulk_address_updates[0]['LAD'])
        test_helper.assertEqual(collection_case['fieldCoordinatorId'],
                                context.bulk_address_updates[0]['FIELDCOORDINATOR_ID'])
        test_helper.assertEqual(collection_case['fieldOfficerId'], context.bulk_address_updates[0]['FIELDOFFICER_ID'])
        test_helper.assertEqual(collection_case['address']['latitude'], context.bulk_address_updates[0]['LATITUDE'])
        test_helper.assertEqual(collection_case['address']['longitude'], context.bulk_address_updates[0]['LONGITUDE'])
        test_helper.assertTrue(collection_case['metadata']['secureEstablishment'],
                               'Secure flag should be changed to true')
        test_helper.assertEqual(collection_case['printBatch'], context.bulk_address_updates[0]['PRINT_BATCH'])
        test_helper.assertEqual(collection_case['ceExpectedCapacity'],
                                int(context.bulk_address_updates[0]['CE_EXPECTED_CAPACITY']))
        test_helper.assertEqual(collection_case['htcWillingness'], context.bulk_address_updates[0]['HTC_WILLINGNESS'])
        test_helper.assertEqual(collection_case['htcDigital'], context.bulk_address_updates[0]['HTC_DIGITAL'])
        test_helper.assertEqual(collection_case['address']['uprn'], context.bulk_address_updates[0]['UPRN'])
        test_helper.assertEqual(collection_case['address']['estabUprn'], context.bulk_address_updates[0]['ESTAB_UPRN'])
        test_helper.assertEqual(collection_case['address']['addressLine1'],
                                context.bulk_address_updates[0]['ADDRESS_LINE1'])
        test_helper.assertEqual(collection_case['address']['addressLine2'],
                                context.bulk_address_updates[0]['ADDRESS_LINE2'])
        test_helper.assertEqual(collection_case['address']['addressLine3'],
                                context.bulk_address_updates[0]['ADDRESS_LINE3'])
        test_helper.assertEqual(collection_case['address']['abpCode'], context.bulk_address_updates[0]['ABP_CODE'])
        test_helper.assertEqual(collection_case['address']['organisationName'],
                                context.bulk_address_updates[0]['ORGANISATION_NAME'])
        test_helper.assertEqual(collection_case['address']['postcode'], context.bulk_address_updates[0]['POSTCODE'])
        test_helper.assertEqual(collection_case['address']['townName'], context.bulk_address_updates[0]['TOWN_NAME'])

        test_helper.assertFalse(collection_case['skeleton'], 'Skeleton flag should be removed from updated case')

    context.bulk_address_updates_file.unlink()
    if Config.BULK_ADDRESS_UPDATE_BUCKET_NAME:
        clear_bucket(Config.BULK_ADDRESS_UPDATE_BUCKET_NAME)


@step('the cases are updated in the database')
def check_the_cases_via_case_api(context):
    for row in context.bulk_address_updates:
        actual_case = get_case_and_case_events_by_case_id(row['CASE_ID'])

        # Check all the fields available in the case API are updated
        test_helper.assertEqual(actual_case['estabType'], row['ESTAB_TYPE'])
        test_helper.assertEqual(actual_case['oa'], row['OA'])
        test_helper.assertEqual(actual_case['lsoa'], row['LSOA'])
        test_helper.assertEqual(actual_case['msoa'], row['MSOA'])
        test_helper.assertEqual(actual_case['lad'], row['LAD'])
        test_helper.assertEqual(actual_case['latitude'], row['LATITUDE'])
        test_helper.assertEqual(actual_case['longitude'], row['LONGITUDE'])
        test_helper.assertTrue(actual_case['secureEstablishment'], 'Secure flag should be changed to true')
        test_helper.assertEqual(actual_case['uprn'], row['UPRN'])
        test_helper.assertEqual(actual_case['estabUprn'], row['ESTAB_UPRN'])
        test_helper.assertEqual(actual_case['addressLine1'], row['ADDRESS_LINE1'])
        test_helper.assertEqual(actual_case['addressLine2'], row['ADDRESS_LINE2'])
        test_helper.assertEqual(actual_case['addressLine3'], row['ADDRESS_LINE3'])
        test_helper.assertEqual(actual_case['abpCode'], row['ABP_CODE'])
        test_helper.assertEqual(actual_case['organisationName'], row['ORGANISATION_NAME'])
        test_helper.assertEqual(actual_case['postcode'], row['POSTCODE'])
        test_helper.assertEqual(actual_case['townName'], row['TOWN_NAME'])


@step('a bulk deactivate uac file is supplied')
def bulk_deactivate_uac_file(context):
    # Build a bulk deactivate uac file
    context.bulk_deactivate_uac_file = RESOURCE_FILE_PATH.joinpath('bulk_processing_files',
                                                                   'deactivate_uac_bulk_test.csv')
    context.bulk_deactivate_uac = []

    for uac_updated in context.uac_created_events:
        context.bulk_deactivate_uac.append(uac_updated['payload']['uac']['questionnaireId'])

    with open(context.bulk_deactivate_uac_file, 'w') as bulk_deactivate_uac_write:
        writer = csv.DictWriter(bulk_deactivate_uac_write, fieldnames=['qid'])
        writer.writeheader()
        for qid in context.bulk_deactivate_uac:
            writer.writerow({'qid': qid})

    # Upload the file to a real bucket if one is configured
    if Config.BULK_DEACTIVATE_UAC_BUCKET_NAME:
        clear_bucket(Config.BULK_DEACTIVATE_UAC_BUCKET_NAME)
        upload_file_to_bucket(context.bulk_deactivate_uac_file,
                              f'deactivate_uacs_acceptance_tests_{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}.csv',
                              Config.BULK_DEACTIVATE_UAC_BUCKET_NAME)


@step('the bulk deactivate file is processed')
def process_bulk_deactivate_uac_file(context):
    # Run against the real bucket if it is configured
    if Config.BULK_REFUSAL_BUCKET_NAME:
        BulkProcessor(DeactivateUacProcessor()).run()
        return

    # If we don't have a bucket, mock the storage bucket client interactions to work with only local files
    with mock_bulk_processor_bucket(context.bulk_deactivate_uac_file):
        BulkProcessor(DeactivateUacProcessor()).run()


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


def patch_download_blob_to_file(_source_blob, local_destination, replacement_local_file: Path):
    # Used to patch the Blob.download_blob_to_file(source_blob, destination) method
    # replacement_local_file must be supplied in a partial so the signatures align
    local_destination.write(replacement_local_file.read_bytes())


@contextmanager
def mock_bulk_processor_bucket(bulk_file: Path):
    # Patch the storage interaction so it works on local files, never a real bucket
    with patch('toolbox.bulk_processing.bulk_processor.storage') as patch_storage:
        patched_storage_client = patch_storage.Client.return_value

        # patch list_blobs to return at least one thing with a .name
        # so that the bulk processor enters it's processing loop and names the files it builds correctly
        mock_blob = Mock(spec=storage.Blob)
        mock_blob.name = bulk_file.name
        patched_storage_client.list_blobs.return_value = [mock_blob]

        # patch the download method so that it writes our local bulk file to the supplied destination
        patched_storage_client.download_blob_to_file.side_effect = partial(
            patch_download_blob_to_file,
            replacement_local_file=bulk_file)

        # Yield here so that within this context the patched bulk processor storage is in effect
        yield


@step("UAC_UPDATED msgs with active set to false for all the original uacs created")
def uac_updated_with_active_set_to_false_for_all_original_uacs(context):
    uac_updated_events = get_uac_updated_events(context, len(context.bulk_deactivate_uac))

    for uac_updated in uac_updated_events:
        test_helper.assertFalse(uac_updated['payload']['uac']['active'])
        context.bulk_deactivate_uac.remove(uac_updated['payload']['uac']['questionnaireId'])

    test_helper.assertEqual(len(context.bulk_deactivate_uac), 0,
                            "Expected to be empty after matching UAC_UPDATED events emitted")


@step("every created UAC QID pair has a DEACTIVATE_UAC event logged against it")
def deactivate_uac_events_logged_against_all_uac_qid_pairs(context):
    for case in context.case_created_events:
        actual_logged_events = get_logged_events_for_case_by_id(case["payload"]["collectionCase"]["id"])
        actual_logged_event_types = [event['eventType'] for event in actual_logged_events]
        test_helper.assertIn('DEACTIVATE_UAC', actual_logged_event_types,
                             msg=(f'Expected event type = {"DEACTIVATE_UAC"},'
                                  f' actual logged event types = {actual_logged_event_types}'))

    if hasattr(context, 'bulk_deactivate_uac_file'):
        context.bulk_deactivate_uac_file.unlink()

    if Config.BULK_DEACTIVATE_UAC_BUCKET_NAME:
        clear_bucket(Config.BULK_DEACTIVATE_UAC_BUCKET_NAME)
