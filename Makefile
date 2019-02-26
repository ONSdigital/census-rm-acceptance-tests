install:
	pipenv install --dev

test:
	pipenv run python run.py --log_level WARN
