from datetime import datetime


def get_datetime_now_as_str():
    return convert_datetime_to_str(datetime.utcnow())


def convert_datetime_to_str(date_time):
    return datetime.strftime(date_time, '%Y-%m-%dT%H:%M:%S.000Z')


def format_date_as_ddmm(date_to_format):
    return '{:02d}'.format(date_to_format.day) + "/" + '{:02d}'.format(date_to_format.month)


def format_period(period_year, period_month):
    return f'{period_year}{str(period_month).zfill(2)}'


def round_to_minute(start_of_test):
    return datetime(start_of_test.year, start_of_test.month,
                    start_of_test.day, start_of_test.hour,
                    start_of_test.minute, second=0, microsecond=0)
