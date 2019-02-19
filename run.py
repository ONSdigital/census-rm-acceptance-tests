import os

from behave import __main__ as behave_executable

if __name__ == '__main__':
    behave_format = os.getenv('BEHAVE_FORMAT', 'progress2')

    behave_executable.main(args=f'--format {behave_format} acceptance_tests/features')
