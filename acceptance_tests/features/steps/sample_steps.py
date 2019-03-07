import json

from behave import when

from utilities.sample_loader.sample_file_loader import load_sample_file


@when('sample file "{sample_file_name}" is loaded')
def load_sample_file_step(context, sample_file_name):
    context.sample_file_name = f'./resources/sample_files/{sample_file_name}'
    sample_units_raw = load_sample_file(context)

    context.sample_units = [
        json.loads(sample_unit)
        for sample_unit in sample_units_raw.values()
    ]

#     _get_sample_units(sample_units_raw)
#
#
# def _get_sample_units(sample_units_raw):

