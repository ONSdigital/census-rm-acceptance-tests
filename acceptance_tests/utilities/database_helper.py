import time

import psycopg2

from config import Config


def poll_database_query_with_timeout(query, query_vars: tuple, result_success_callback, timeout=60):
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
