from behave import fixture

# from acceptance_tests.features.pages import sign_out_internal
# from common.collection_exercise_utilities import create_business_survey_period, create_social_survey_period, \
#     execute_collection_exercises, generate_collection_exercise_dates_from_period, \
#     generate_new_enrolment_code_from_existing_code, make_user_description, create_variable_collection_exercise_dates
# from common.internal_user_utilities import create_internal_user_login_account
# from common.respondent_utilities import create_enrolled_respondent_for_the_test_survey, create_respondent, \
#     create_respondent_data, create_respondent_email_address, create_respondent_user_login_account, \
#     create_ru_reference, \
#     create_unenrolled_respondent, create_unverified_respondent, register_respondent
# from common.survey_utilities import create_survey_reference, create_test_survey, format_survey_name, is_social_survey, \
#     logger
# from config import Config
# from controllers import collection_exercise_controller
from datetime import datetime, timedelta
from utilities.collection_exercise_utilities import create_collection_exercise
from utilities.id_generation import create_survey_ref
from utilities.survey_utilities import create_survey_classifier, create_survey

# COLLECTION_EXERCISE_CREATED = 'CREATED'
# COLLECTION_EXERCISE_SCHEDULED = 'SCHEDULED'
# COLLECTION_EXERCISE_READY_FOR_REVIEW = 'READY_FOR_REVIEW'
# COLLECTION_EXERCISE_READY_FOR_LIVE = 'READY_FOR_LIVE'
# COLLECTION_EXERCISE_LIVE = 'LIVE'


@fixture
def setup_create_census_survey(context):

    survey_data = create_data_for_census_survey(context, legal_basis ='STA1947')

    context.survey_ref = survey_data['survey_ref'],
    # context.period = survey_data['period'],
    # context.legal_basis = survey_data['legal_basis'],
    # context.short_name = context.survey_ref,
    # context.long_name = context.survey_ref,
    # context.survey_type = survey_data['survey_type']

    context.survey_ref = "111",
    context.period = '201901',
    context.legal_basis = 'STA1947',
    context.short_name = '111',
    context.long_name = '111',
    context.survey_type = 'Social'

    survey_ref = context.survey_ref

    survey_response = create_survey(context.survey_ref, context.short_name, context.long_name, context.legal_basis, context.survey_type)
    context.survey_id = survey_response.json()['id']

    survey_classifier_response = create_survey_classifier(context.survey_id)
    context.classifier_id = survey_classifier_response.json()['id']


# @fixture
# def setup_create_census_collection_exercise(context):
#     collex_response = create_collection_exercise(context.survey_ref, period)
#
#     context.collection_exercise_id = get_collection_exercise_id_from_response(collex_response)
#
#     mandatory_events = generate_collection_exercise_dates(datetime.now() + timedelta(weeks=1))
#
#     create_mandatory_events(context.collection_exercise_id, mandatory_events)


def create_data_for_census_survey(context, legal_basis):
    """ Data used for creating a Survey """
    period_offset_days = getattr(context, 'period_offset_days', 0)

    survey_ref = create_survey_ref()
    period = create_survey_period(period_offset_days=period_offset_days)

    # return {
    #     'survey_ref': 'a',
    #     'period': 'a',
    #     'legal_basis': 'a',
    #     'short_name': 'a',
    #     'long_name': 'a',
    #     'survey_type': 'a'
    # }
    return {
        'survey_ref': create_survey_ref(),
        'period': period,
        'legal_basis': legal_basis,
        'short_name': survey_ref,
        'long_name': survey_ref,
        'survey_type': 'Social'
    }


# def create_data_for_collection_exercise():
#     """ Data used for creating a Collection Exercise """
#     return {
#         'survey_ref': create_survey_reference()
#     }
#
def create_survey_period(period_offset_days=0):
    period_date = datetime.utcnow() + timedelta(days=period_offset_days)

    return format_period(period_date.year, period_date.month)


def create_social_survey_period(period_offset_days=0):
    period_date = datetime.utcnow() + timedelta(days=period_offset_days)

    return format_period(period_date.year, period_date.month)


def format_period(period_year, period_month):
    return f'{period_year}{str(period_month).zfill(2)}'



# def create_default_data(context, eq_ci=False):
#     logger.debug(
#         f'Feature [{context.feature_name}], Scenario [{context.scenario_name}] creating default Survey & Exercise')
#
#     survey_type = context.survey_type
#     scenario_name = context.scenario_name
#
#     survey_data = create_data_for_survey(context)
#
#     period = survey_data['period']
#     legal_basis = survey_data['legal_basis']
#     short_name = survey_data['short_name']
#     long_name = survey_data['long_name']
#     survey_ref = create_data_for_collection_exercise()['survey_ref']
#
#     survey_id = create_test_survey(long_name, short_name, survey_ref, context.survey_type, legal_basis)
#
#     if is_social_survey(context.survey_type):
#         context.iac = create_test_social_collection_exercise(context, survey_id, period, short_name, scenario_name,
#                                                              survey_type)
#     else:
#         response = create_test_business_collection_exercise(survey_id, period, short_name, scenario_name,
#                                                             survey_type, eq_ci=eq_ci)
#         context.iac = response['iac']
#
#     # Save values for later
#     context.period = period
#     context.legal_basis = legal_basis
#     context.short_name = short_name
#     context.long_name = long_name
#     context.survey_ref = survey_ref
#     context.survey_id = survey_id
#     context.respondent_email = create_respondent_email_address(short_name)
#
#
# def create_test_social_collection_exercise(context, survey_id, period, ru_ref, ce_name, survey_type):
#     """ Creates a new Collection Exercise for the survey supplied """
#
#     logger.debug('Creating Social Collection Exercise', survey_id=survey_id, period=period)
#
#     user_description = make_user_description(ce_name, is_social_survey(survey_type), 50)
#     dates = generate_collection_exercise_dates_from_period(period)
#
#     iac = collection_exercise_controller.create_and_execute_social_collection_exercise(context, survey_id, period,
#                                                                                        user_description, dates,
#                                                                                        short_name=ru_ref)
#
#     logger.debug('Social Collection Exercise created - ', survey_id=survey_id, ru_ref=ru_ref,
#                  user_description=user_description, period=period, dates=dates)
#
#     return iac
#
#
# def create_test_business_collection_exercise(survey_id, period, ru_ref, ce_name, survey_type, stop_at_state='LIVE',
#                                              eq_ci=False):
#     """ Creates a new Collection Exercise for the survey supplied """
#
#     logger.debug('Creating Business Collection Exercise', survey_id=survey_id, period=period)
#
#     user_desc = make_user_description(ce_name, is_social_survey(survey_type), 50)
#     dates = generate_collection_exercise_dates_from_period(period)
#
#     response = collection_exercise_controller.create_and_execute_collection_exercise_with_unique_sample(survey_id,
#                                                                                                         period,
#                                                                                                         user_desc,
#                                                                                                         dates, ru_ref,
#                                                                                                         stop_at_state,
#                                                                                                         eq_ci=eq_ci)
#
#     logger.debug('Business Collection Exercise created - ', survey_id=survey_id, ru_ref=ru_ref,
#                  user_desc=user_desc, period=period, dates=dates)
#
#     return {'collection_exercise': response['collection_exercise'],
#             'iac': response['iac'],
#             'user_description': user_desc,
#             'dates': dates}
