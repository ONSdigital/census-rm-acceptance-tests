import logging
from structlog import wrap_logger
from config import Config
import requests

from datetime import datetime, timedelta

from utilities.collection_exercise_utilities import create_collection_exercise
from utilities.id_generation import create_survey_ref
from utilities.survey_utilities import create_survey, create_survey_classifier

logger = wrap_logger(logging.getLogger(__name__))


def create_census_survey(context):

    survey_data = create_data_for_survey(context)

    context.survey_ref = survey_data['survey_ref']
    context.legal_basis = survey_data['legal_basis']
    context.short_name= survey_data['short_name']
    context.long_name = survey_data['long_name']
    context.survey_type = survey_data['survey_type']

    context.survey_id = create_survey(context.survey_ref, context.short_name, context.long_name, context.legal_basis, context.survey_type)['id']
    context.classifier_id = create_survey_classifier(context.survey_id)['id']


def create_census_collection_exercise(context):
    survey_collection_exercise_data = create_data_for_collection_exercise()
    context.period = survey_collection_exercise_data['period']

    context.dates = generate_collection_exercise_dates_from_period(context.period)

    response = create_business_collection_exercise_to_scheduled_state(context.survey_id, context.period, context.survey_ref,
                                                                      context.dates)

    context.collection_exercise_id = response['id']
    context.user_description = response['userDescription']


def create_data_for_survey(context):
    """ Data used for creating a Survey """
    period_offset_days = getattr(context, 'period_offset_days', 0)

    survey_ref = create_survey_ref()

    return {
        'survey_ref': survey_ref,
        'legal_basis': 'STA1947',
        'short_name': survey_ref,
        'long_name': survey_ref,
        'survey_type': 'Social'
    }


def post_event_to_collection_exercise(collection_exercise_id, event_tag, date_str):
    logger.debug('Adding a collection exercise event',
                 collection_exercise_id=collection_exercise_id, event_tag=event_tag)

    url = f'{Config.COLLECTION_EXERCISE_SERVICE}/collectionexercises/{collection_exercise_id}/events'
    post_data = {'tag': event_tag, 'timestamp': date_str}
    response = requests.post(url, auth=Config.BASIC_AUTH, json=post_data)
    # 409: event already exists, which we count as permissable for testing
    if response.status_code not in (201, 409):
        logger.error('Failed to post event', status=response.status_code)
        raise Exception(f'Failed to post event {collection_exercise_id}')

    logger.debug('Successfully added event', collection_exercise_id=collection_exercise_id, event_tag=event_tag)

def create_data_for_collection_exercise():
    """ Data used for creating a Collection Exercise """
    return {
        'period' : create_survey_period()
    }


def create_business_collection_exercise(survey_id, period, user_description):
    create_collection_exercise(survey_id, period, user_description)

    return get_collection_exercise(survey_id, period)


def create_business_collection_exercise_to_created_state(survey_id, period, user_description):
    return create_business_collection_exercise(survey_id, period, user_description)


def create_business_collection_exercise_to_scheduled_state(survey_id, period, user_description, dates):
    collection_exercise = create_business_collection_exercise_to_created_state(survey_id, period, user_description)
    collection_exercise_id = collection_exercise['id']

    post_event_to_collection_exercise(collection_exercise_id, 'mps',
                                      convert_datetime_for_event(dates['mps']))
    post_event_to_collection_exercise(collection_exercise_id, 'go_live',
                                      convert_datetime_for_event(dates['go_live']))
    post_event_to_collection_exercise(collection_exercise_id, 'ref_period_start',
                                      convert_datetime_for_event(dates['go_live']))
    post_event_to_collection_exercise(collection_exercise_id, 'return_by',
                                      convert_datetime_for_event(dates['return_by']))
    post_event_to_collection_exercise(collection_exercise_id, 'ref_period_end',
                                      convert_datetime_for_event(dates['return_by']))
    post_event_to_collection_exercise(collection_exercise_id, 'exercise_end',
                                      convert_datetime_for_event(dates['exercise_end']))
    return collection_exercise


# def create_business_collection_exercise_to_ready_for_review_state(survey_id, period, user_description, dates, ru_ref):
#     collection_exercise = create_business_collection_exercise_to_scheduled_state(survey_id, period, user_description,
#                                                                                  dates)
#     collection_exercise_id = collection_exercise['id']
#
#     # upload_response = sample_controller.upload_unique_sample(collection_exercise_id, ru_ref)
#     #
#     # sample_summary = upload_response['upload_response']
#     #
#     # link_sample_summary_to_collection_exercise(collection_exercise_id, sample_summary['id'])
#     #
#     # ci_controller.load_and_link_eq_collection_instrument(survey_id, collection_exercise_id,
#     #                                                     'resources/collection_instrument_files/064_201803_0001.xlsx')
#
#     create_ci = create_eq_collection_instrument(context.survey_id, form_type="household", eq_id="census")
#
#     ci_response = get_collection_instruments_by_classifier(survey_id=context.survey_id, form_type="household")
#     context.collection_instrument_id = ci_response[0]['id']
#
#     link_response = link_ci_to_exercise(context.collection_instrument_id, context.collection_exercise_id)
#
#     return collection_exercise


def generate_collection_exercise_dates_from_period(period):
    """Generates a collection exercise events base date from the period supplied."""

    now = datetime.utcnow()
    period_year = int(period[:4])
    period_month = int(period[-2:])

    base_date = datetime(period_year, period_month, now.day, now.hour, now.minute, now.second, now.microsecond)

    return generate_collection_exercise_dates(base_date)


def generate_collection_exercise_dates(base_date):
    """Generates and returns collection exercise event dates based on the base date supplied."""

    dates = {
        'mps': base_date + timedelta(seconds=5),
        'go_live': base_date + timedelta(minutes=1),
        'return_by': base_date + timedelta(days=10),
        'exercise_end': base_date + timedelta(days=11)
    }

    return dates


def create_survey_period(period_offset_days=0):
    period_date = datetime.utcnow() + timedelta(days=period_offset_days)

    return format_period(period_date.year, period_date.month)


def convert_datetime_for_event(date_time):
    return datetime.strftime(date_time, '%Y-%m-%dT%H:%M:%S.000Z')


def create_social_survey_period(period_offset_days=0):
    period_date = datetime.utcnow() + timedelta(days=period_offset_days)

    return format_period(period_date.year, period_date.month)


def format_period(period_year, period_month):
    return f'{period_year}{str(period_month).zfill(2)}'


def get_collection_exercise(survey_id, period):
    logger.debug('Retrieving collection exercise', survey_id=survey_id, exercise_ref=period)
    url = f'{Config.COLLECTION_EXERCISE_SERVICE}/collectionexercises/survey/{survey_id}'
    response = requests.get(url=url, auth=Config.BASIC_AUTH)
    response.raise_for_status()
    collection_exercises = response.json()
    for ce in collection_exercises:
        if ce['exerciseRef'] == period:
            collection_exercise = ce
            break
    else:
        return None
    logger.debug('Successfully retrieved collection exercise', survey_id=survey_id, exercise_ref=period)
    return collection_exercise


# def create_test_business_collection_exercise(survey_id, period, ru_ref, ce_name, survey_type, stop_at_state='LIVE',
#                                              eq_ci=False):
#     """ Creates a new Collection Exercise for the survey supplied """
#
#     logger.debug('Creating Business Collection Exercise', survey_id=survey_id, period=period)
#
#     user_desc = make_user_description(ce_name, is_social_survey(survey_type), 50)
#     dates = generate_collection_exercise_dates_from_period(period)
#
#     response = collection_exercise_controller.create_and_execute_collection_exercise_with_unique_sample(survey_id,
#                                                                                                         period,
#                                                                                                         user_desc,
#                                                                                                         dates, ru_ref,
#                                                                                                         stop_at_state,
#                                                                                                         eq_ci=eq_ci)
#
#     logger.debug('Business Collection Exercise created - ', survey_id=survey_id, ru_ref=ru_ref,
#                  user_desc=user_desc, period=period, dates=dates)
#
#     return {'collection_exercise': response['collection_exercise'],
#             'iac': response['iac'],
#             'user_description': user_desc,
#             'dates': dates}
