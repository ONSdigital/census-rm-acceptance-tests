from datetime import datetime

import paramiko

from config import Config
from acceptance_tests.utilities.date_utilities import round_to_minute


class SftpUtility:
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
        self._sftp_client = self.ssh_client.open_sftp()
        return self

    def __exit__(self, *_):
        self.ssh_client.close()

    def get_files_filtered_by_survey_ref_period_and_modified_date(self, start_of_test):
        files = self._sftp_client.listdir_attr(Config.SFTP_DIR)
        start_of_test = round_to_minute(start_of_test)
        period = start_of_test.strftime('%Y-%m-%d')
        return list(filter(lambda f: f'P_IC_ICL1_{period}' in f.filename
                                     and start_of_test <= datetime.fromtimestamp(f.st_mtime), files))

    def get_files_content_as_list(self, files):
        actual_content = []

        for _file in files:
            file_path = f'{Config.SFTP_DIR}/{_file.filename}'
            content_list = self._get_file_lines_as_list(file_path)
            actual_content.extend(content_list)

        return actual_content

    def _get_file_lines_as_list(self, file_path):
        with self._sftp_client.open(file_path) as sftp_file:
            content = sftp_file.read().decode('utf-8')
            return content.rstrip().split('\n')
