import logging

import requests
from behave import given, when, then
from structlog import wrap_logger
from utilities.actions import create_action_plan
from utilities.case import get_cases

from utilities.collection_exercise_utilities import create_collection_exercise, \
    get_collection_exercise_id_from_response, create_mandatory_events
from utilities.database import reset_database
from utilities.sample_loader.sample_file_loader import load_sample_file
from utilities.survey_utilities import create_survey, create_survey_classifier
from utilities.collection_instrument_utilities import create_eq_collection_instrument, \
    get_collection_instruments_by_classifier, link_ci_to_exercise
from utilities.date_utilities import get_timestamp_with_offset

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
    logger.debug("Successfully added survey classifier", classifier_id=context.classifier_id)

    collex_response = create_collection_exercise(context.survey_ref)
    assert collex_response.status_code == requests.codes.created
    logger.debug("Successfully created collection exercise", exercise_ref=context.survey_ref)
    context.collection_exercise_id = get_collection_exercise_id_from_response(collex_response)

    # Temp dates
    mandatory_events = {
        "mps": get_timestamp_with_offset(months=0, weeks=1),
        "go_live": get_timestamp_with_offset(months=0, weeks=1, hours=1),
        "return_by": get_timestamp_with_offset(months=0, weeks=1, hours=2),
        "exercise_end":get_timestamp_with_offset(months=0, weeks=1, hours=3)
    }

    event_status = create_mandatory_events(context.collection_exercise_id, mandatory_events)

    for status in event_status:
        assert status == requests.codes.created

    create_ci = create_eq_collection_instrument(context.survey_id, form_type="household", eq_id="census")
    assert create_ci.status_code == requests.codes.ok

    ci_response = get_collection_instruments_by_classifier(survey_id=context.survey_id, form_type="household")
    assert len(ci_response[0]['id']) == 36
    context.collection_instrument_id = ci_response[0]['id']

    link_response = link_ci_to_exercise(context.collection_instrument_id, context.collection_exercise_id)
    assert link_response.status_code == requests.codes.ok

    action_response, context.action_plan_id = create_action_plan(context.survey_ref, context.collection_exercise_id)
    assert action_response.status_code == requests.codes.created
    logger.debug("Successfully created action plan")


@when('a sample file "{sample_file_name}" is loaded')
def load_sample_file_step(context, sample_file_name):
    sample_file_path = f'./resources/sample_files/{sample_file_name}'

    context.sample_file_name = sample_file_path
    load_sample_file(context)


@then("a call to the casesvc api returns {expected_row_count:d} cases")
def check_count_of_cases(context, expected_row_count):
    cases_response = get_cases(expected_row_count)
    assert cases_response.status_code == requests.codes.ok

    assert len(cases_response.json()) == expected_row_count


def set_ids(context, scenario_id):
    context.scenario_id = scenario_id
    context.survey_ref = 'Census' + context.scenario_id


@given("the database is cleared down")
def the_database_is_cleared_down(context):
    reset_database()
