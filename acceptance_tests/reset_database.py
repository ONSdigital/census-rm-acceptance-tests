from acceptance_tests import database_controller


def reset_database():
    print('Resetting databases')
    database_controller.execute_sql('resources/database/database_reset_rm.sql')
    print('Reset DB')


if __name__ == '__main__':
    reset_database()
