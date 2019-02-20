from datetime import datetime


def convert_datetime_for_event(date_time):
    return datetime.strftime(date_time, '%Y-%m-%dT%H:%M:%S.000Z')


def format_period(period_year, period_month):
    return f'{period_year}{str(period_month).zfill(2)}'
