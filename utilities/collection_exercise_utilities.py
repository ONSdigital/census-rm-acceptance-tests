import logging
import requests

from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def create_collection_exercise(survey_ref):
    collex = {
        "surveyRef": survey_ref,
        "name": survey_ref[:20],
        "exerciseRef": '1',
        "userDescription": '1',
    }

    response = requests.post(f"{Config.COLLECTION_EXERCISE_SERVICE}/collectionexercises",
                             auth=Config.BASIC_AUTH, json=collex)

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