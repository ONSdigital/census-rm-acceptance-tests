import logging

from sqlalchemy import create_engine
from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def execute_sql(sql_script_file_path=None, sql_string=None, database_uri=Config.DATABASE_URI):
    logger.debug('Executing SQL script', sql_script_file_path=sql_script_file_path)
    engine = create_engine(database_uri, connect_args={"options": "-c statement_timeout=120000"})
    connection = engine.connect()
    trans = connection.begin()

    if sql_script_file_path:
        with open(sql_script_file_path, 'r') as sqlScriptFile:
            sql = sqlScriptFile.read().replace('\n', '')
    else:
        sql = sql_string

    response = connection.execute(sql)

    trans.commit()
    logger.debug('Successfully executed SQL script', sql_script_file_path=sql_script_file_path)
    return response
