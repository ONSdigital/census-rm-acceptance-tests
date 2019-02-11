import subprocess

import requests
from behave import given, when, then
import logging

from structlog import wrap_logger

from utilities.collection_exercise_utilities import create_collection_exercise, get_collection_exercise_id_from_response
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


@when('a sample file "{sample_file_name}" is loaded')
def step_impl(context, sample_file_name):
    context.sample_file_name = sample_file_name
    load_sample_file(context)


@then('"{10}" Rows appear on the case database')
def step_impl(context, expected_row_count):
    # Test database table case has expected_row_count
    pass


def load_sample_file(context):
    result = subprocess.run('pwd', stdout=subprocess.PIPE)

    p = subprocess.Popen(['python', 'load_sample.py', context.sample_file_name, context.collection_exercise_id,
                             'NoActionPlanIDForThisTest', context.classifier_id],
                         cwd='../census-rm-sample-loader')
    p.wait()

    #result = subprocess.run(['python', 'census-rm-sample-loader/load_sample.py'], stdout=subprocess.PIPE)

    #x = subprocess.call(["python", "census-rm-sample-loader/load_sample.py"], stdout=subprocess.PIPE)


    # result = subprocess.run(['cd census-rm-sample-loader']
    #
    # result = subprocess.run(['cd census-rm-sample-loader; python load_sample.py', context.sample_file_name, context.collection_exercise_id,
    #                          'NoActionPlanIDForThisTest', context.classifier_id], stdout=subprocess.PIPE)
    a = 1


def set_ids(context, scenario_id):
    context.scenario_id = scenario_id
    context.survey_ref = 'Census' + context.scenario_id


@given("the database is cleared down")
def the_database_is_cleared_down(context):
    reset_database()
