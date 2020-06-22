import time

import psycopg2

from config import Config


def poll_database_query_with_timeout(query, query_vars: tuple, result_success_callback, timeout=60):
    """
    :param query: The database query to execute
    :param query_vars: Query parameters to pass to the query executor
    :param result_success_callback: A result checking callback function, should return true for success, false for
    failure and fail the tests to break if the timeout deadline is exceeded (it might seem unintuitive that the callback
    checks the timeout but this lets it log the failure reason with access to the data for better failure reporting)
    expected signature: example(db_result, timeout_deadline) -> bool
    :param timeout: Timeout period in second
    :return: None
    """
    conn = psycopg2.connect(f"dbname='{Config.DB_NAME}' user={Config.DB_USERNAME} host='{Config.DB_HOST}' "
                            f"password={Config.DB_PASSWORD} port='{Config.DB_PORT}'{Config.DB_USESSL}")
    timeout_deadline = time.time() + timeout
    cur = conn.cursor()
    while True:
        cur.execute(query, vars=query_vars)
        db_result = cur.fetchall()
        if result_success_callback(db_result, timeout_deadline):
            return
        time.sleep(1)
