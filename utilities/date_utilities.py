from datetime import datetime
import maya
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import tzlocal


def get_timestamp():
    return maya.now().iso8601()


def get_timestamp_with_offset(months, weeks):
    future = datetime.now() + relativedelta(months=months, weeks=weeks)
    return maya.MayaDT.from_datetime(future).iso8601()


def parse_timestamp(date):
    future = parse(date)
    return maya.MayaDT.from_datetime(future).iso8601()


def parse_timestamp_with_timezone(date, timezone):
    return maya.parse(date).datetime(to_timezone=timezone, native=False)


def convert_to_iso_timestamp(timestamp_string):
    timestamp = datetime.strptime(timestamp_string, "%Y-%m-%dT%H:%M")
    timestamp_iso = timestamp.astimezone(tzlocal.get_localzone()).isoformat(timespec='milliseconds')
    return timestamp_iso