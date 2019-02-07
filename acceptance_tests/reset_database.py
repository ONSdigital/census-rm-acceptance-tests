from utilities import database


def reset_database():
    print('Resetting databases')
    database.execute_sql('resources/database/database_reset_rm.sql')
    print('Reset DB')


if __name__ == '__main__':
    reset_database()
