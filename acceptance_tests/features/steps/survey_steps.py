from datetime import datetime

import pika
from behave import given

from acceptance_tests.data_setup.action_setup import get_id_of_1st_action_plan_for_collection_excercise
from acceptance_tests.data_setup.collection_exercise_setup import setup_census_collection_exercise
from acceptance_tests.data_setup.survey_setup import setup_census_survey
from config import Config


@given('a survey exists with a collection exercise')
def a_survey_exists_with_collex(context):
    context.test_start_local_datetime = datetime.now()
    setup_census_survey(context)
    setup_census_collection_exercise(context)
    context.action_plan_id = get_id_of_1st_action_plan_for_collection_excercise(context.collection_exercise_id)
    _purge_queues()


def _purge_queues():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=Config.RABBITMQ_HOST, port=Config.RABBITMQ_PORT))

    channel = connection.channel()
    channel.queue_purge(queue=Config.RABBITMQ_RH_OUTBOUND_QUEUE)
    channel.queue_purge(queue=Config.RABBITMQ_CASE_INBOUND_JSON_QUEUE)
