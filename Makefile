install:
	pipenv install --dev

package_vulnerability:
	PIPENV_PYUP_API_KEY="" pipenv check

flake:
	pipenv run flake8 .

lint: flake

check: package_vulnerability flake

# Put back this: package_vulnerability
test:  flake at_tests

smoke_test: package_vulnerability flake run_smoke_tests

regression_test: package_vulnerability flake run_regression_tests

at_tests:
	SFTP_KEY_FILENAME=dummy_sftp_private_key PUBSUB_EMULATOR_HOST=localhost:8538 pipenv run python run.py --log_level WARN

run_regression_tests:
	SFTP_KEY_FILENAME=dummy_sftp_private_key PUBSUB_EMULATOR_HOST=localhost:8538 pipenv run behave acceptance_tests/features --logging-level WARN --format=progress2

run_smoke_tests:
	SFTP_KEY_FILENAME=dummy_sftp_private_key PUBSUB_EMULATOR_HOST=localhost:8538 pipenv run behave acceptance_tests/features --logging-level WARN --tags=@smoke --no-skipped

build:
	docker build -t eu.gcr.io/census-rm-ci/rm/census-rm-acceptance-tests .
