import hashlib
import json

from acceptance_tests.utilities.mappings import PACK_CODE_TO_SFTP_DIRECTORY, PACK_CODE_TO_DESCRIPTION, \
    PACK_CODE_TO_DATASET
from acceptance_tests.utilities.sftp_utility import SftpUtility
from acceptance_tests.utilities.test_case_helper import test_helper


def check_manifest_files_created(context, pack_code):
    with SftpUtility() as sftp_utility:
        files = sftp_utility.get_all_files_after_time(context.test_start_local_datetime, pack_code)

        for _file in files:
            if _file.filename.endswith(".csv.gpg"):
                csv_file = _file
                manifest_file = _get_matching_manifest_file(csv_file.filename, files)

                if manifest_file is None:
                    test_helper.fail(f'Failed to find manifest file for {csv_file.filename}')

                actual_manifest = _get_actual_manifest(sftp_utility, manifest_file, pack_code)
                creation_datetime = actual_manifest['manifestCreated']
                expected_manifest = _create_expected_manifest(sftp_utility, csv_file, creation_datetime, pack_code)
                test_helper.assertDictEqual(actual_manifest, expected_manifest)


def _get_matching_manifest_file(filename, files):
    manifest_filename = filename.replace(".csv.gpg", ".manifest")

    for _file in files:
        if _file.filename == manifest_filename:
            return _file

    return None


def _get_actual_manifest(sftp_utility, manifest_file, pack_code):
    actual_manifest_json = sftp_utility.get_file_contents_as_string(f'{PACK_CODE_TO_SFTP_DIRECTORY[pack_code]}/'
                                                                    f'{manifest_file.filename}')
    return json.loads(actual_manifest_json)


def _create_expected_manifest(sftp_utility, csv_file, created_datetime, pack_code):
    actual_file_contents = sftp_utility.get_file_contents_as_string(f'{PACK_CODE_TO_SFTP_DIRECTORY[pack_code]}'
                                                                    f'/{csv_file.filename}')
    decrypted_file_contents = sftp_utility.decrypt_message(actual_file_contents)

    md5_hash = hashlib.md5(actual_file_contents.encode('utf-8')).hexdigest()
    expected_size = sftp_utility.get_file_size(f'{PACK_CODE_TO_SFTP_DIRECTORY[pack_code]}/{csv_file.filename}')

    _file = dict(
        sizeBytes=str(expected_size),
        md5sum=md5_hash,
        relativePath='./',
        name=csv_file.filename,
        rows=len(decrypted_file_contents.splitlines())
    )

    manifest = dict(
        schemaVersion='1',
        files=[_file],
        sourceName="ONS_RM",
        manifestCreated=created_datetime,
        description=PACK_CODE_TO_DESCRIPTION[pack_code],
        dataset=PACK_CODE_TO_DATASET[pack_code],
        version='1'
    )

    return manifest
