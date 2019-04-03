import pika

from acceptance_tests.utilities.sample_loader.exceptions import RabbitConnectionClosedError
from config import Config


class RabbitContext:

    def __init__(self, **kwargs):
        self._host = kwargs.get('host') or Config.RABBITMQ_HOST
        self._port = kwargs.get('port') or Config.RABBITMQ_PORT
        self._vhost = kwargs.get('vhost') or Config.RABBITMQ_VHOST
        self._exchange = kwargs.get('exchange') or Config.RABBITMQ_EXCHANGE
        self._user = kwargs.get('user') or Config.RABBITMQ_USER
        self._password = kwargs.get('password') or Config.RABBITMQ_PASSWORD
        self.queue_name = kwargs.get('queue_name') or Config.RABBITMQ_QUEUE

    def __enter__(self):
        self._open_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.close()

    def _open_connection(self):
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(self._host,
                                      self._port,
                                      self._vhost,
                                      pika.PlainCredentials(self._user, self._password)))
        self._channel = self._connection.channel()

        if self.queue_name == 'localtest':
            self._channel.queue_declare(queue=self.queue_name)

    def publish_message(self, message: str, content_type: str):
        if not self._connection.is_open:
            raise RabbitConnectionClosedError
        self._channel.basic_publish(exchange=self._exchange,
                                    routing_key=self.queue_name,
                                    body=message,
                                    properties=pika.BasicProperties(content_type=content_type))
