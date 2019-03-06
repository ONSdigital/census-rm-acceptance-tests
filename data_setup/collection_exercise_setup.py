import logging
from datetime import datetime, timedelta
from json import dumps, loads

import requests
from structlog import wrap_logger

from config import Config
from controllers.collection_exercise_controller import post_event_to_collection_exercise, create_collection_exercise, \
    get_collection_exercise
from utilities.date_utilities import convert_datetime_for_event, format_period

logger = wrap_logger(logging.getLogger(__name__))


def setup_census_collection_exercise_to_scheduled_state(context):
    survey_collection_exercise_data = _create_data_for_collection_exercise()
    context.period = survey_collection_exercise_data['period']

    dates = _generate_collection_exercise_dates_from_period(context.period)
    context.collex_return_by_date = get_formatted_expected_return_by_date_for_print_file(dates)

    context.collection_exercise_id = setup_collection_exercise_to_scheduled_state(context.survey_id, context.period,
                                                                                  context.survey_ref, dates)['id']
    create_ci = create_eq_collection_instrument(context.survey_id, form_type="household", eq_id="census")
    assert create_ci.status_code == requests.codes.ok

    ci_response = get_collection_instruments_by_classifier(survey_id=context.survey_id, form_type="household")
    assert len(ci_response[0]['id']) == 36
    context.collection_instrument_id = ci_response[0]['id']

    link_response = link_ci_to_exercise(context.collection_instrument_id, context.collection_exercise_id)
    assert link_response.status_code == requests.codes.ok


def get_formatted_expected_return_by_date_for_print_file(dates):
    return_by_date = dates["return_by"]
    return '{:02d}'.format(return_by_date.day) + "/" + '{:02d}'.format(return_by_date.month)


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
        'mps': base_date + timedelta(seconds=10),
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


def create_eq_collection_instrument(survey_id, form_type, eq_id):
    logger.debug('Uploading eQ collection instrument', survey_id=survey_id, form_type=form_type)
    url = f'{Config.COLLECTION_INSTRUMENT_SERVICE}/' \
          f'collection-instrument-api/1.0.2/upload'

    classifiers = {
        "form_type": form_type,
        "eq_id": eq_id
    }

    params = {
        "classifiers": dumps(classifiers),
        "survey_id": survey_id
    }
    response = requests.post(url=url, auth=Config.BASIC_AUTH, params=params)
    response.raise_for_status()
    logger.debug('Successfully uploaded eQ collection instrument', survey_id=survey_id, form_type=form_type)
    return response


def get_collection_instruments_by_classifier(survey_id=None, form_type=None):
    logger.debug('Retrieving collection instruments', survey_id=survey_id, form_type=form_type)
    url = f'{Config.COLLECTION_INSTRUMENT_SERVICE}/' \
          f'collection-instrument-api/1.0.2/collectioninstrument'

    classifiers = dict()

    if survey_id:
        classifiers['SURVEY_ID'] = survey_id
    if form_type:
        classifiers['form_type'] = form_type

    response = requests.get(url=url, auth=Config.BASIC_AUTH, params={'searchString': dumps(classifiers)})

    response.raise_for_status()

    logger.debug('Successfully retrieved collection instruments', survey_id=survey_id, form_type=form_type)
    return loads(response.text)


def link_ci_to_exercise(collection_instrument_id, collection_exercise_id):
    logger.debug('Linking collection instrument to exercise',
                 collection_instrument_id=collection_instrument_id, collection_exercise_id=collection_exercise_id)
    url = f'{Config.COLLECTION_INSTRUMENT_SERVICE}/' \
          f'collection-instrument-api/1.0.2/link-exercise/{collection_instrument_id}/{collection_exercise_id}'

    response = requests.post(url=url, auth=Config.BASIC_AUTH)
    response.raise_for_status()

    logger.debug('Successfully linked collection instrument to exercise',
                 collection_instrument_id=collection_instrument_id, collection_exercise_id=collection_exercise_id)
    return response
