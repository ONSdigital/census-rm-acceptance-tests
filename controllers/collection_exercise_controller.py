import logging

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


def get_collection_exercise(survey_id, period):
    logger.info('Retrieving collection exercise', survey_id=survey_id, exercise_ref=period)

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

    logger.info('Successfully retrieved collection exercise', survey_id=survey_id, exercise_ref=period)

    return collection_exercise
