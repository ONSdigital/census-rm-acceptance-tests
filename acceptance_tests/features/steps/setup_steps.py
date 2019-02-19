import json
import logging

import requests
from behave import given, when, then
from structlog import wrap_logger

from acceptance_tests.features.data_setup import create_census_survey, create_census_collection_exercise
from utilities.actions import create_action_plan
from utilities.case import get_all_cases_from_casesvc
from utilities.database import reset_database
from utilities.sample_loader.sample_file_loader import load_sample_file

logger = wrap_logger(logging.getLogger(__name__))


@given('a survey exists')
def a_survey_exists(context):
    create_census_survey(context)


@given('a collection exercise exists')
def a_collection_exercise_exists(context):
    create_census_collection_exercise(context)

    action_response, context.action_plan_id = create_action_plan(context.survey_ref, context.collection_exercise_id)


@when('a sample file "{sample_file_name}" is loaded')
def load_sample_file_step(context, sample_file_name):
    sample_file_path = f'./resources/sample_files/{sample_file_name}'

    context.sample_file_name = sample_file_path
    context.sample_units = load_sample_file(context)


@then("a call to the casesvc api returns {expected_row_count:d} cases")
def check_count_of_cases(context, expected_row_count):
    sample_units = [
        json.loads(sample_unit).get('id')
        for sample_unit in context.sample_units.values()
    ]

    cases_response = get_all_cases_from_casesvc(sample_units)

    assert len(cases_response) == expected_row_count


def set_ids(context, scenario_id):
    context.scenario_id = scenario_id
    context.survey_ref = 'Census' + context.scenario_id


@given("the database is cleared down")
def the_database_is_cleared_down(context):
    reset_database()


# def create_data_for_census_survey(context, legal_basis):
#     """ Data used for creating a Survey """
#     period_offset_days = getattr(context, 'period_offset_days', 0)
#
#     survey_ref = create_survey_ref()
#     period = create_survey_period(period_offset_days=period_offset_days)
#
#     return {
#         'survey_ref': survey_ref,
#         'period': period,
#         'legal_basis': legal_basis,
#         'short_name': survey_ref,
#         'long_name': survey_ref,
#         'survey_type': 'Social'
#     }
#

# def setup_create_census_survey(context, survey_data2):
#
#     survey_data = create_data_for_census_survey(context, legal_basis ='STA1947')
#
#     context.survey_ref = survey_data['survey_ref'],
#     context.period = survey_data['period'],
#     context.legal_basis = survey_data['legal_basis'],
#     context.short_name = context.survey_ref,
#     context.long_name = context.survey_ref,
#     context.survey_type = survey_data['survey_type']
#
#     # context.survey_ref2 = survey_data2['survey_ref'],
#     # context.period2 = survey_data2['period'],
#     # context.legal_basis2 = survey_data2['legal_basis'],
#     # context.short_name2 = context.survey_ref,
#     # context.long_name2 = context.survey_ref,
#     # context.survey_type2 = survey_data2['survey_type']
#     #
#     #
#     # context.survey_ref = "111",
#     # context.period = '201901',
#     # context.legal_basis = 'STA1947',
#     # context.short_name = '111',
#     # context.long_name = '111',
#     # context.survey_type = 'Social'
#     #
#     # survey_ref = context.survey_ref
#     # period = survey_data['period']
#
#     survey_response = create_survey(context.survey_ref, context.short_name, context.long_name, context.legal_basis, context.survey_type)
#     context.survey_id = survey_response.json()['id']
#
#     survey_classifier_response = create_survey_classifier(context.survey_id)
#     context.classifier_id = survey_classifier_response.json()['id']
#
# def create_survey_period(period_offset_days=0):
#     period_date = datetime.utcnow() + timedelta(days=period_offset_days)
#
#     return format_period(period_date.year, period_date.month)
#
#
# def create_social_survey_period(period_offset_days=0):
#     period_date = datetime.utcnow() + timedelta(days=period_offset_days)
#
#     return format_period(period_date.year, period_date.month)
#
#
# def format_period(period_year, period_month):
#     return f'{period_year}{str(period_month).zfill(2)}'
