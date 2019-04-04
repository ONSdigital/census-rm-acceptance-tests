from datetime import datetime, timedelta


def convert_datetime_to_str(date_time):
    return datetime.strftime(date_time, '%Y-%m-%dT%H:%M:%S.000Z')


def create_period(period_offset_days=0):
    period_date = datetime.utcnow() + timedelta(days=period_offset_days)
    return f'{period_date.year}{str(period_date.month).zfill(2)}'


def round_to_minute(start_of_test):
    return datetime(start_of_test.year, start_of_test.month,
                    start_of_test.day, start_of_test.hour,
                    start_of_test.minute, second=0, microsecond=0)
