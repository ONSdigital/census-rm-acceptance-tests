import argparse
import logging

from behave import __main__ as behave_executable

DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_BEHAVE_FORMAT = 'progress2'
DEFAULT_FEATURE_DIRECTORY = 'acceptance_tests/features'


def parse_arguments():
    """
    Parses commandline arguments
    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser('Run behave scenarios')
    parser.add_argument('--log_level', '-l', help='Logging level', default=DEFAULT_LOG_LEVEL)
    parser.add_argument('--format', '-f', help='Behave format', default=DEFAULT_BEHAVE_FORMAT)
    parser.add_argument('--feature_directory', '-fd', help='Feature directory', default=DEFAULT_FEATURE_DIRECTORY)

    return parser.parse_args()


def main():
    """
    Runner
    """
    args = parse_arguments()

    logging.basicConfig(level=args.log_level)

    behave_executable.main(args=f'--logging-level {args.log_level} --format {args.format} {args.feature_directory}')


if __name__ == '__main__':
    main()
