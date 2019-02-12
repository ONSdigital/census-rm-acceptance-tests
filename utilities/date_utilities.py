from datetime import datetime
import maya
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


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
