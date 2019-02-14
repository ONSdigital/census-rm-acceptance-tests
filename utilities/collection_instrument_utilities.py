import logging
import requests
from json import dumps, loads

from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def create_eq_collection_instrument(survey_id, form_type, eq_id):
    logger.debug('Uploading eQ collection instrument', survey_id=survey_id, form_type=form_type)
    url = f'{Config.COLLECTION_INSTRUMENT_SERVICE}/collection-instrument-api/1.0.2/upload'

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
    url = f'{Config.COLLECTION_INSTRUMENT_SERVICE}/collection-instrument-api/1.0.2/collectioninstrument'

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
