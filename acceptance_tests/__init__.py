from pathlib import Path

# Resources directory, 1 level outside the acceptance tests module in <project_root>/resources
RESOURCE_FILE_PATH = Path(__file__).parents[1].joinpath('resources')
