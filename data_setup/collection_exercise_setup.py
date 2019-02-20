import logging
from datetime import datetime, timedelta

from structlog import wrap_logger

from controllers.collection_exercise_controller import post_event_to_collection_exercise, create_collection_exercise, \
    get_collection_exercise
from utilities.date_utilities import convert_datetime_for_event, format_period

logger = wrap_logger(logging.getLogger(__name__))


def setup_census_collection_exercise_to_scheduled_state(context):
    survey_collection_exercise_data = _create_data_for_collection_exercise()
    period = survey_collection_exercise_data['period']

    dates = _generate_collection_exercise_dates_from_period(period)

    context.collection_exercise_id = setup_collection_exercise_to_scheduled_state(context.survey_id, period,
                                                                                  context.survey_ref, dates)['id']


def setup_collection_exercise_to_created_state(survey_id, period, user_description):
    create_collection_exercise(survey_id, period, user_description)

    return get_collection_exercise(survey_id, period)


def setup_collection_exercise_to_scheduled_state(survey_id, period, user_description, dates):
    collection_exercise = setup_collection_exercise_to_created_state(survey_id, period, user_description)
    collection_exercise_id = collection_exercise['id']

    post_event_to_collection_exercise(collection_exercise_id, 'mps',
                                      convert_datetime_for_event(dates['mps']))
    post_event_to_collection_exercise(collection_exercise_id, 'go_live',
                                      convert_datetime_for_event(dates['go_live']))
    post_event_to_collection_exercise(collection_exercise_id, 'return_by',
                                      convert_datetime_for_event(dates['return_by']))
    post_event_to_collection_exercise(collection_exercise_id, 'exercise_end',
                                      convert_datetime_for_event(dates['exercise_end']))
    return collection_exercise


def _generate_collection_exercise_dates_from_period(period):
    now = datetime.utcnow()
    period_year = int(period[:4])
    period_month = int(period[-2:])

    base_date = datetime(period_year, period_month, now.day, now.hour, now.minute, now.second, now.microsecond)

    return _generate_collection_exercise_dates(base_date)


def _generate_collection_exercise_dates(base_date):
    return {
        'mps': base_date + timedelta(seconds=5),
        'go_live': base_date + timedelta(minutes=1),
        'return_by': base_date + timedelta(days=10),
        'exercise_end': base_date + timedelta(days=11)
    }


def _create_survey_period(period_offset_days=0):
    period_date = datetime.utcnow() + timedelta(days=period_offset_days)

    return format_period(period_date.year, period_date.month)


def _create_data_for_collection_exercise():
    return {
        'period': _create_survey_period()
    }
