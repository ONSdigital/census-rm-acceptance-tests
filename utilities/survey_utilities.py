import logging
import requests

from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))

def create_survey(survey_ref, short_name, long_name, legal_basis, survey_type):
    logger.debug('Creating new survey',
                 survey_ref=survey_ref, short_name=short_name,
                 long_name=long_name, legal_basis=legal_basis,
                 survey_type=survey_type)

    url = f'{Config.SURVEY_SERVICE}/surveys'

    survey_details = {
        "surveyRef": survey_ref,
        "longName": long_name,
        "shortName": short_name,
        "legalBasisRef": legal_basis,
        "surveyType": survey_type
    }

    response = requests.post(url, json=survey_details, auth=Config.BASIC_AUTH)
    response.raise_for_status()

    return response


def create_survey_classifier(survey_id):
    url = f'{Config.SURVEY_SERVICE}/surveys/{survey_id}/classifiers'
    classifiers = {"name": "COLLECTION_INSTRUMENT", "classifierTypes": ["COLLECTION_EXERCISE"]}

    response = requests.post(url, auth=Config.BASIC_AUTH, json=classifiers)
    response.raise_for_status()

    return response


