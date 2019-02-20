from behave import when

from utilities.sample_loader.sample_file_loader import load_sample_file


@when('a sample file "{sample_file_name}" is loaded')
def load_sample_file_step(context, sample_file_name):
    context.sample_file_name = f'./resources/sample_files/{sample_file_name}'
    context.sample_units = load_sample_file(context)
