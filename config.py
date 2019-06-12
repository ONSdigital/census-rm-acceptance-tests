import os


class Config:

    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME', 'admin')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD', 'secret')
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)

    DATABASE_URI = os.getenv('DATABASE_URI', "postgres://postgres:postgres@localhost:6432/postgres")
    AUTH_DATABASE_URI = os.getenv('AUTH_DATABASE_URI', DATABASE_URI)
    PARTY_DATABASE_URI = os.getenv('PARTY_DATABASE_URI', DATABASE_URI)
    COLLECTION_INSTRUMENT_DATABASE_URI = os.getenv('COLLECTION_INSTRUMENT_DATABASE_URI', DATABASE_URI)
    SECURE_MESSAGE_DATABASE_URI = os.getenv('SECURE_MESSAGE_DATABASE_URI', DATABASE_URI)

    PROTOCOL = os.getenv('PROTOCOL', 'http')

    ACTION_SERVICE_HOST = os.getenv('ACTION_SERVICE_HOST', 'localhost')
    ACTION_SERVICE_PORT = os.getenv('ACTION_SERVICE_PORT', 8301)
    ACTION_SERVICE = f'{PROTOCOL}://{ACTION_SERVICE_HOST}:{ACTION_SERVICE_PORT}'

    SURVEY_SERVICE_HOST = os.getenv('SURVEY_SERVICE_HOST', 'localhost')
    SURVEY_SERVICE_PORT = os.getenv('SURVEY_SERVICE_PORT', 8080)
    SURVEY_SERVICE = f'{PROTOCOL}://{SURVEY_SERVICE_HOST}:{SURVEY_SERVICE_PORT}'

    COLLECTION_EXERCISE_SERVICE_HOST = os.getenv('COLLECTION_EXERCISE_SERVICE_HOST', 'localhost')
    COLLECTION_EXERCISE_SERVICE_PORT = os.getenv('COLLECTION_EXERCISE_SERVICE_PORT', 8145)
    COLLECTION_EXERCISE_SERVICE = f'{PROTOCOL}://{COLLECTION_EXERCISE_SERVICE_HOST}:{COLLECTION_EXERCISE_SERVICE_PORT}'

    COLLECTION_INSTRUMENT_SERVICE_HOST = os.getenv('COLLECTION_INSTRUMENT_SERVICE_HOST', 'localhost')
    COLLECTION_INSTRUMENT_SERVICE_PORT = os.getenv('COLLECTION_INSTRUMENT_SERVICE_PORT', 8002)
    COLLECTION_INSTRUMENT_SERVICE = f'{PROTOCOL}://{COLLECTION_INSTRUMENT_SERVICE_HOST}:' \
                                    f'{COLLECTION_INSTRUMENT_SERVICE_PORT}'

    CASE_SERVICE_HOST = os.getenv('CASE_SERVICE_HOST', 'localhost')
    CASE_SERVICE_PORT = os.getenv('CASE_SERVICE_PORT', 8171)
    CASE_SERVICE = f'{PROTOCOL}://{CASE_SERVICE_HOST}:{CASE_SERVICE_PORT}'

    RABBITMQ_HOST = os.getenv('RABBITMQ_SERVICE_HOST', 'localhost')
    RABBITMQ_PORT = os.getenv('RABBITMQ_SERVICE_PORT', '6672')
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')
    RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', 'case.sample.inbound')
    RABBITMQ_RH_OUTBOUND_CASE_QUEUE = os.getenv('RABBITMQ_RH_OUTBOUND_CASE_QUEUE', 'case.rh.case')
    RABBITMQ_RH_OUTBOUND_UAC_QUEUE = os.getenv('RABBITMQ_RH_OUTBOUND_UAC_QUEUE', 'case.rh.uac')
    RABBITMQ_OUTBOUND_FIELD_QUEUE = os.getenv('RABBITMQ_OUTBOUND_FIELD_QUEUE', 'Action.Field')
    RABBITMQ_INBOUND_EQ_QUEUE = os.getenv('RABBITMQ_INBOUND_EQ_QUEUE', 'Case.Responses')
    RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', '')
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')

    REDIS_HOST = os.getenv('REDIS_SERVICE_HOST', 'localhost')
    REDIS_PORT = os.getenv('REDIS_SERVICE_PORT', '7379')
    REDIS_DB = os.getenv('REDIS_DB', '0')

    SFTP_HOST = os.getenv('SFTP_HOST', 'localhost')
    SFTP_PORT = os.getenv('SFTP_PORT', '122')
    SFTP_USERNAME = os.getenv('SFTP_USERNAME', 'centos')
    SFTP_PASSWORD = os.getenv('SFTP_PASSWORD', 'JLibV2&XD,')
    SFTP_DIR = os.getenv('SFTP_DIR', 'Documents/sftp/print_service')

    RECEIPT_TOPIC_PROJECT = os.getenv('RECEIPT_TOPIC_PROJECT', 'project')
    RECEIPT_TOPIC_ID = os.getenv('RECEIPT_TOPIC_ID', 'eq-submission-topic')

    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')

    CASEAPI_SERVICE_HOST = os.getenv('CASEAPI_SERVICE_HOST', 'localhost')
    CASEAPI_SERVICE_PORT = os.getenv('CASEAPI_SERVICE_PORT', '8161')
    CASEAPI_SERVICE = f'{PROTOCOL}://{CASEAPI_SERVICE_HOST}:{CASEAPI_SERVICE_PORT}'
