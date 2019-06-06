install:
	pipenv install --dev

package_vulnerability:
	pipenv check

flake:
	pipenv run flake8 .

test: package_vulnerability flake at_tests

at_tests:
	USE_LOCAL_DOCKER=True pipenv run python run.py --log_level WARN
