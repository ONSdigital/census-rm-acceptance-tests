from datetime import datetime, timedelta
import maya
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import tzlocal


def get_timestamp():
    return maya.now().iso8601()


def get_timestamp_with_offset(base_date, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0, microseconds=0):
    future = base_date + relativedelta(months=months, weeks=weeks, days=days, hours=hours,
                                            minutes=minutes, seconds=seconds, microseconds=microseconds)
    date_str = future.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    return date_str + 'Z'


def parse_timestamp(date):
    """ This class can accept various string formats for the date
        Examples:
        '2018-06-29 08:15:27.243860',
        'Jun 28 2018  7:40AM',
        'Jun 28 2018 at 7:40AM',
        'September 18, 2017, 22:19:55',
        'Sun, 05/12/1999, 12:30PM',
        'Mon, 21 March, 2015',
        '2018-03-12T10:12:45Z',
        '2018-06-29 17:08:00.586525+00:00',
        '2018-06-29 17:08:00.586525+05:00',
        'Tuesday , 6th September, 2017 at 4:30pm'
    """
    future = parse(date)
    return maya.MayaDT.from_datetime(future).iso8601()


def parse_timestamp_with_timezone(date, timezone):
    return maya.parse(date).datetime(to_timezone=timezone, native=False)


def convert_to_iso_timestamp(timestamp_string):
    timestamp = datetime.strptime(timestamp_string, "%Y-%m-%dT%H:%M")
    timestamp_iso = timestamp.astimezone(tzlocal.get_localzone()).isoformat(timespec='milliseconds')
    return timestamp_iso


def generate_collection_exercise_dates(base_date):
    """Generates and returns collection exercise event dates based on the base date supplied."""

    dates = {
        'mps': get_timestamp_with_offset(base_date + timedelta(seconds=5)),
        'go_live': get_timestamp_with_offset(base_date + timedelta(minutes=1)),
        'return_by': get_timestamp_with_offset(base_date + timedelta(days=10)),
        'exercise_end': get_timestamp_with_offset(base_date + timedelta(days=11))
    }

    return dates
