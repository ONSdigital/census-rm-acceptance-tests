from datetime import datetime, timedelta

from behave import given

from acceptance_tests.data_setup.action_setup import create_action_rule


@given('an action rule of type {action_type} is set {action_rule_delay} seconds in the future')
def setup_action_rule(context, action_type, action_rule_delay):
    create_action_rule(context.survey_ref, f'{context.survey_ref} {action_type}', action_type,
                       datetime.utcnow() + timedelta(seconds=int(action_rule_delay)),
                       context.action_plan_id)
