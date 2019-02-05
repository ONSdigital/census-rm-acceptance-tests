import os


class Config(object):

    PROTOCOL = os.getenv('PROTOCOL', 'http')

    ACTION_SERVICE_HOST = os.getenv('ACTION_SERVICE_HOST', 'actionsvc')
    ACTION_SERVICE_PORT = os.getenv('ACTION_SERVICE_PORT', 80)
    ACTION_SERVICE = f'{PROTOCOL}://{ACTION_SERVICE_HOST}:{ACTION_SERVICE_PORT}'
