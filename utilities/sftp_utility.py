import paramiko

from config import Config


def create_open_sftp_client():
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=Config.SFTP_HOST,
                       port=int(Config.SFTP_PORT),
                       username=Config.SFTP_USERNAME,
                       password=Config.SFTP_PASSWORD,
                       look_for_keys=False,
                       timeout=120)
    return ssh_client.open_sftp()
