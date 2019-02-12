from datetime import datetime
import maya
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


def get_timestamp():
    return maya.now().iso8601()


def get_timestamp_with_offset(months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0, microseconds=0):
    future = datetime.now() + relativedelta(months=months, weeks=weeks, days=days, hours=hours,
                                            minutes=minutes, seconds=seconds, microseconds=microseconds)
    date_str = future.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    return date_str + 'Z'

# Example date string to parse is 'April 29 2018 05:15'
def parse_timestamp(date):
    future = parse(date)
    return maya.MayaDT.from_datetime(future).iso8601()


def parse_timestamp_with_timezone(date, timezone):
    return maya.parse(date).datetime(to_timezone=timezone, native=False)