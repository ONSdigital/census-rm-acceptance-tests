import logging
import requests

from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def create_collection_exercise(survey_id, exercise_ref, user_description):
    create_collection_exercise_url = f'{Config.COLLECTION_EXERCISE}/collectionexercises'
    collex = {
        "surveyId": survey_id,
        "exerciseRef": exercise_ref,
        "userDescription": user_description
    }
    response = requests.post(create_collection_exercise_url, auth=Config.BASIC_AUTH, json=collex)
    response.raise_for_status()
    response_json = response.json()
    logger.debug("Successfully created collection exercise", exercise_ref=exercise_ref)
    return response_json


def delete_collection_exercise(id):
    # TODO: DELETE /collectionexercises/id
    pass