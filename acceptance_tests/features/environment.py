import os
from datetime import datetime
from logging import getLogger

from behave import use_fixture
from structlog import wrap_logger

from acceptance_tests.features.fixtures import setup_create_census_survey
from exceptions import MissingFixtureError

FIXTURE_TAG_PREFIX = 'fixture.'

logger = wrap_logger(getLogger(__name__))

fixture_scenario_registry = {
    'fixture.create.survey':
        setup_create_census_survey
}


def process_scenario_fixtures(context):
    for tag in context.all_tags:
        if tag.startswith(FIXTURE_TAG_PREFIX):
            try:
                use_fixture(fixture_scenario_registry[tag], context)
            except KeyError:
                raise MissingFixtureError


def before_feature(context, feature):
    context.feature_name = feature.name
    context.all_tags = feature.tags


def before_scenario(context, scenario):
    context.scenario_name = scenario.name
    context.all_tags.extend(scenario.tags)

    # # Run any custom scenario setup from fixture tags
    process_scenario_fixtures(context)
