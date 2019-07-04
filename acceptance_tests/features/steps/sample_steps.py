import json

from behave import step
from load_sample import load_sample_file


@step('sample file "{sample_file_name}" is loaded')
def load_sample_file_step(context, sample_file_name):
    sample_file_name = f'./resources/sample_files/{sample_file_name}'
    sample_units_raw = load_sample_file(sample_file_name, context.collection_exercise_id,
                                        context.action_plan_id)

    context.sample_units = [
        json.loads(sample_unit)
        for sample_unit in sample_units_raw.values()
    ]
