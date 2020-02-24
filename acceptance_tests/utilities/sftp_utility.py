import base64
from datetime import datetime

import paramiko
import pgpy

from acceptance_tests.utilities.mappings import PACK_CODE_TO_SFTP_DIRECTORY
from config import Config


class SftpUtility:
    def __init__(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh_client.connect(hostname=Config.SFTP_HOST,
                                port=int(Config.SFTP_PORT),
                                username=Config.SFTP_USERNAME,
                                key_filename=Config.SFTP_KEY_FILENAME,
                                passphrase=Config.SFTP_PASSPHRASE,
                                look_for_keys=False,
                                timeout=120)

    def __enter__(self):
        self._sftp_client = self.ssh_client.open_sftp()
        return self

    def __exit__(self, *_):
        self.ssh_client.close()

    def get_all_files_after_time(self, period_start_time, prefix, suffix=""):
        files = self._sftp_client.listdir_attr(PACK_CODE_TO_SFTP_DIRECTORY[prefix])
        period = period_start_time.strftime('%Y-%m-%d')

        return [
                _file for _file in files
                if f'{prefix}_{period}' in _file.filename
                and _file.filename.endswith(suffix)
                and period_start_time <= datetime.fromtimestamp(_file.st_mtime)
            ]

    def get_files_content_as_list(self, files, prefix):
        actual_content = []

        for _file in files:
            file_path = f'{PACK_CODE_TO_SFTP_DIRECTORY[prefix]}/{_file.filename}'
            content_list = self._get_file_lines_as_list(file_path)
            actual_content.extend(content_list)

        return actual_content

    def _get_file_lines_as_list(self, file_path):
        with self._sftp_client.open(file_path) as sftp_file:
            content = sftp_file.read().decode('utf-8')
            decrypted_content = self.decrypt_message(content)
            return decrypted_content.rstrip().split('\n')

    def get_file_contents_as_string(self, file_path):
        with self._sftp_client.open(file_path) as sftp_file:
            return sftp_file.read().decode('utf-8')

    def get_file_size(self, file_path):
        return self._sftp_client.lstat(file_path).st_size

    def decrypt_message(self, message):
        our_key, _ = pgpy.PGPKey.from_file('our_dummy_private.asc')
        with our_key.unlock('test'):
            encrypted_text_message = pgpy.PGPMessage.from_blob(message)
            message_text = our_key.decrypt(encrypted_text_message)

            return message_text.message
