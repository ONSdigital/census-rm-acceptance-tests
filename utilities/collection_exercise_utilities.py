import logging
import requests

from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def create_collection_exercise(survey_ref):
    collex = {
        "surveyRef": survey_ref,
        "exerciseRef": '1',
        "userDescription": '1',
    }

    url = f"{Config.COLLECTION_EXERCISE_SERVICE}/collectionexercises"

    response = requests.post(url, auth=Config.BASIC_AUTH, json=collex)

    response.raise_for_status()

    return response


def get_collection_exercise_id_from_response(response):
    headers = response.headers
    store = headers.__getattribute__('_store')
    collection_exercise_uri = store['location'][1]

    return collection_exercise_uri.rsplit('/', 1)[-1]


def delete_collection_exercise(id):
    # TODO: DELETE /collectionexercises/id
    pass


def create_collex_event(collection_exercise_id, event_tag, timestamp):
    logger.debug('Adding a collection exercise event',
                 collection_exercise_id=collection_exercise_id, event_tag=event_tag)

    collex_event_url = f"{Config.COLLECTION_EXERCISE_SERVICE}/collectionexercises/{collection_exercise_id}/events"
    eventTag = {
        "tag": event_tag,
        "timestamp": timestamp
    }

    response = requests.post(collex_event_url, auth=Config.BASIC_AUTH, json=eventTag)
    response.raise_for_status()
    if response.status_code == requests.codes.created:
        logger.debug('Event created', collection_exercise_id=collection_exercise_id, event_tag=event_tag)
    return response.status_code


def create_mandatory_events(collection_exercise_id, collex_events: dict):
    logger.debug('Creating mandatory events', collection_exercise_id=collection_exercise_id)
    url = f"{Config.COLLECTION_EXERCISE_SERVICE}/collectionexercises/{collection_exercise_id}/events"

    return_statuses = []

    for event, timestamp in collex_events.items():
        event_tag = {
            'tag': event,
            'timestamp': timestamp
        }

        response = requests.post(url, auth=Config.BASIC_AUTH, json=event_tag)
        response.raise_for_status()
        
        if response.status_code == requests.codes.created:
            logger.debug('Event created', collection_exercise_id=collection_exercise_id, event_tag=event_tag)
        else:
            logger.debug('Event not created', collection_exercise_id=collection_exercise_id, event_tag=event_tag)

        return_statuses.append(response.status_code)

    return return_statuses
