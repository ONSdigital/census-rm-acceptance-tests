import os
import sys
from logging import getLogger

from behave import __main__ as behave_executable
from structlog import wrap_logger

from utilities.database import reset_database

logger = wrap_logger(getLogger(__name__))


if __name__ == '__main__':
    # reset_database()

    behave_format = os.getenv('BEHAVE_FORMAT', 'progress2')

    behave_executable.main(args=f'--format {behave_format} acceptance_tests/features')
