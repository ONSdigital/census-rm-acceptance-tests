from datetime import datetime

import paramiko

from config import Config
from utilities.date_utilities import round_to_minute


class SFTPUtility():
    def __init__(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname=Config.SFTP_HOST,
                           port=int(Config.SFTP_PORT),
                           username=Config.SFTP_USERNAME,
                           password=Config.SFTP_PASSWORD,
                           look_for_keys=False,
                           timeout=120)

    def __enter__(self):
        self.__sftp_client = self.ssh_client.open_sftp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ssh_client.close()

    def get_files_filtered_by_survey_ref_period_and_modified_date(self, survey_ref, period, start_of_test):
        files = self.__sftp_client.listdir_attr(Config.SFTP_DIR)
        start_of_test = round_to_minute(start_of_test)

        return list(filter(lambda f: f'{survey_ref}_{period}' in f.filename
                                     and start_of_test <= datetime.fromtimestamp(f.st_mtime), files))

    def get_files_content_as_list(self, files):
        actual_content = []

        # Can this be done in a nicer way?
        for file in files:
            file_path = f'{Config.SFTP_DIR}/{file.filename}'
            content_list = self._get_file_lines_as_list(file_path)
            actual_content.extend(content_list)

        return actual_content

    def _get_file_lines_as_list(self, file_path):
        with self.__sftp_client.open(file_path) as sftp_file:
            content = sftp_file.read().decode('utf-8')
            return content.rstrip().split('\n')
