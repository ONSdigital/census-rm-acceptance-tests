import os
import sys
from logging import getLogger

from behave import __main__ as behave_executable
from structlog import wrap_logger

logger = wrap_logger(getLogger(__name__))


if __name__ == '__main__':

    behave_format = os.getenv('BEHAVE_FORMAT', 'progress2')

    behave_executable.main(args=f'--format {behave_format} acceptance_tests/features')
