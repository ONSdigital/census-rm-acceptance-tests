import maya
from dateutil.parser import parse


def create_utc_timestamp():
    return maya.now().iso8601()


def create_timestamp(month, day, year, time):
    date = parse(month )
