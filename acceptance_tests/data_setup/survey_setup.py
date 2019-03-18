from acceptance_tests.controllers.survey_controller import create_survey, create_survey_classifiers
from acceptance_tests.utilities.string_utilities import create_random_string


def setup_census_survey(context):
    survey_data = _create_data_for_survey()

    context.survey_ref = survey_data['survey_ref']
    context.legal_basis = survey_data['legal_basis']
    context.short_name = survey_data['short_name']
    context.long_name = survey_data['long_name']
    context.survey_type = survey_data['survey_type']

    context.survey_id = create_survey(context.survey_ref, context.short_name, context.long_name,
                                      context.legal_basis, context.survey_type)['id']

    survey_classifiers = {"name": "COLLECTION_INSTRUMENT", "classifierTypes": ["COLLECTION_EXERCISE"]}
    create_survey_classifiers(context.survey_id, survey_classifiers)['id']


def _create_data_for_survey():
    survey_ref = create_survey_ref()

    return {
        'survey_ref': survey_ref,
        'legal_basis': 'STA1947',
        'short_name': survey_ref,
        'long_name': survey_ref,
        'survey_type': 'Social'
    }


def create_survey_ref():
    survey_ref = create_random_string(min_len=13, max_len=13)

    return f'Census-{survey_ref}'
