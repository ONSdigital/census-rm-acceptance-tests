from datetime import datetime, timedelta

from controllers.collection_exercise_controller import post_event_to_collection_exercise, create_collection_exercise, \
    create_eq_collection_instrument, get_collection_instruments_by_classifier, \
    link_ci_to_exercise
from utilities.date_utilities import convert_datetime_to_str, create_period


def setup_census_collection_exercise(context):
    context.period = create_period()

    context.dates = _generate_collection_exercise_dates_from_period(context.period)
    create_eq_collection_instrument  context.collection_exercise_id = _setup_collection_exercise_to_scheduled_state(context.survey_id, context.period,
                                                                                   context.survey_ref,
                                                                                   context.dates)
    context.collection_instrument_id = _add_a_collection_instrument(context)


def _setup_collection_exercise_to_scheduled_state(survey_id, period, user_description, dates):
    collection_exercise_id = create_collection_exercise(survey_id, period, user_description)

    post_event_to_collection_exercise(collection_exercise_id, 'mps',
                                      convert_datetime_to_str(dates['mps']))
    post_event_to_collection_exercise(collection_exercise_id, 'go_live',
                                      convert_datetime_to_str(dates['go_live']))
    post_event_to_collection_exercise(collection_exercise_id, 'return_by',
                                      convert_datetime_to_str(dates['return_by']))
    post_event_to_collection_exercise(collection_exercise_id, 'exercise_end',
                                      convert_datetime_to_str(dates['exercise_end']))
    return collection_exercise_id


def _generate_collection_exercise_dates_from_period(period):
    now = datetime.utcnow()
    period_year = int(period[:4])
    period_month = int(period[-2:])

    base_date = datetime(period_year, period_month, now.day, now.hour, now.minute, now.second, now.microsecond)

    return _generate_collection_exercise_dates(base_date)


def _add_a_collection_instrument(context):
    create_eq_collection_instrument(context.survey_id, form_type="household", eq_id="census")
    collection_instrument_id = get_collection_instruments_by_classifier(survey_id=context.survey_id,
                                                                        form_type="household")[0]['id']
    link_ci_to_exercise(collection_instrument_id, context.collection_exercise_id)

    return collection_instrument_id


def _generate_collection_exercise_dates(base_date):
    return {
        'mps': base_date + timedelta(seconds=10),
        'go_live': base_date + timedelta(minutes=1),
        'return_by': base_date + timedelta(days=10),
        'exercise_end': base_date + timedelta(days=11)
    }
