from typing import Mapping

import redis

from acceptance_tests.utilities.sample_loader.exceptions import RedisPipelineClosedError
from config import Config


class RedisPipelineContext:

    def __init__(self, **kwargs):
        self._host = kwargs.get('host') or Config.REDIS_HOST
        self._port = kwargs.get('port') or Config.REDIS_PORT
        self._db = kwargs.get('db') or Config.REDIS_DB
        self._is_pipeline_open = False

    def __enter__(self):
        self._open_pipeline()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._execute_pipeline()

    def _open_pipeline(self):
        self._connection = redis.StrictRedis(host=self._host, port=self._port, db=self._db)
        self._pipeline = self._connection.pipeline()
        self._is_pipeline_open = True

    def _execute_pipeline(self):
        self._is_pipeline_open = False
        self._pipeline.execute()

    def set_names_to_values(self, names_to_values: Mapping[str, str]):
        if not self._is_pipeline_open:
            raise RedisPipelineClosedError
        for name, value in names_to_values.items():
            self._pipeline.set(name=name, value=value)
