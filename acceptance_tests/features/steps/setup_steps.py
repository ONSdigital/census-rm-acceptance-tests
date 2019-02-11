import subprocess

import requests
from behave import given, when, then
import logging

from structlog import wrap_logger

from utilities.collection_exercise_utilities import create_collection_exercise, get_collection_exercise_id_from_response, create_mandatory_events
from utilities.database import reset_database
from utilities.survey_utilities import create_survey, create_survey_classifier

logger = wrap_logger(logging.getLogger(__name__))


@given('there is a live collection exercise with unique id "{unique_id}"')
def there_is_a_live_collex(context, unique_id):
    set_ids(context, unique_id)

    survey_response = create_survey(context.survey_ref, context.survey_ref, context.survey_ref,
                                    'GovERD', 'Social')
    assert survey_response.status_code == requests.codes.created
    context.survey_id = survey_response.json()['id']
    logger.debug("Successfully created survey", short_name=context.survey_ref)

    survey_classifier_response = create_survey_classifier(context.survey_id)
    assert survey_classifier_response.status_code == requests.codes.created
    context.classifier_id = survey_classifier_response.json()['id']
    logger.debug("Successfully added survey classifier", classifier_id=context.classifier_id )

    collex_response = create_collection_exercise(context.survey_ref)
    assert collex_response.status_code == requests.codes.created
    logger.debug("Successfully created collection exercise", exercise_ref=context.survey_ref)
    context.collection_exercise_id = get_collection_exercise_id_from_response(collex_response)

    # Temp dates
    mandatory_events = {
        "mps": "2019-02-08T15:00:00.000Z",
        "go_live": "2019-02-08T16:00:00.000Z",
        "return_by": "2019-02-08T17:00:00.000Z",
        "exercise_end": "2019-02-08T18:00:00.000Z"
    }

    event_status = create_mandatory_events(context.collection_exercise_id, mandatory_events)

    for status in event_status:
        assert status == requests.codes.created



@when('a sample file "{sample_file_name}" is loaded')
def step_impl(context, sample_file_name):
    load_sample_file(sample_file_name)


@then('"{10}" Rows appear on the case database')
def step_impl(context, expected_row_count):
    # Test database table case has expected_row_count
    pass


def load_sample_file(sample_file_name):
    pass


def set_ids(context, scenario_id):
    context.scenario_id = scenario_id
    context.survey_ref = 'Census' + context.scenario_id


@given("the database is cleared down")
def the_database_is_cleared_down(context):
    reset_database()
