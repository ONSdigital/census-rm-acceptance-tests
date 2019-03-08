import logging
from json import dumps, loads

import requests
from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def create_collection_exercise(survey_id, period, user_description):
    logger.info('Creating collection exercise', survey_id=survey_id, period=period, user_description=user_description)

    url = f'{Config.COLLECTION_EXERCISE_SERVICE}/collectionexercises'

    json = {
        "surveyId": survey_id,
        "exerciseRef": period,
        "userDescription": user_description
    }

    response = requests.post(url, auth=Config.BASIC_AUTH, json=json)
    response.raise_for_status()

    logger.info('Successfully created collection exercise', survey_id=survey_id, period=period,
                user_description=user_description)

    return _get_collection_exercise_id_from_response(response)


def _get_collection_exercise_id_from_response(response):
    collection_exercise_uri = response.headers.__getattribute__('_store')['location'][1]
    return collection_exercise_uri.rsplit('/', 1)[-1]


def create_eq_collection_instrument(survey_id, form_type, eq_id):
    logger.info('Uploading eQ collection instrument', survey_id=survey_id, form_type=form_type)

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

    logger.info('Successfully uploaded eQ collection instrument', survey_id=survey_id, form_type=form_type)

    return response


def get_collection_instruments_by_classifier(survey_id=None, form_type=None):
    logger.info('Retrieving collection instruments', survey_id=survey_id, form_type=form_type)

    url = f'{Config.COLLECTION_INSTRUMENT_SERVICE}/' \
          f'collection-instrument-api/1.0.2/collectioninstrument'

    classifiers = dict()

    if survey_id:
        classifiers['SURVEY_ID'] = survey_id
    if form_type:
        classifiers['form_type'] = form_type

    response = requests.get(url=url, auth=Config.BASIC_AUTH, params={'searchString': dumps(classifiers)})

    response.raise_for_status()

    logger.info('Successfully retrieved collection instruments', survey_id=survey_id, form_type=form_type)

    return loads(response.text)


def link_ci_to_exercise(collection_instrument_id, collection_exercise_id):
    logger.info('Linking collection instrument to exercise',
                collection_instrument_id=collection_instrument_id, collection_exercise_id=collection_exercise_id)

    url = f'{Config.COLLECTION_INSTRUMENT_SERVICE}/' \
          f'collection-instrument-api/1.0.2/link-exercise/{collection_instrument_id}/{collection_exercise_id}'

    response = requests.post(url=url, auth=Config.BASIC_AUTH)
    response.raise_for_status()

    logger.info('Successfully linked collection instrument to exercise',
                collection_instrument_id=collection_instrument_id, collection_exercise_id=collection_exercise_id)

    return response


def post_event_to_collection_exercise(collection_exercise_id, event_tag, date_str):
    logger.info('Adding a collection exercise event',
                collection_exercise_id=collection_exercise_id, event_tag=event_tag, date_str=date_str)

    url = f'{Config.COLLECTION_EXERCISE_SERVICE}/collectionexercises/{collection_exercise_id}/events'
    post_data = {'tag': event_tag, 'timestamp': date_str}

    response = requests.post(url, auth=Config.BASIC_AUTH, json=post_data)

    # 409: event already exists, which we count as permissable for testing
    if response.status_code not in (201, 409):
        logger.error('Failed to post event', status=response.status_code)
        raise Exception(f'Failed to post event {collection_exercise_id}')

    logger.info('Successfully added event', collection_exercise_id=collection_exercise_id, event_tag=event_tag,
                date_str=date_str)
