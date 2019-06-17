install:
	pipenv install --dev

package_vulnerability:
	pipenv check

flake:
	pipenv run flake8 .

test: package_vulnerability flake at_tests

at_tests:
	SFTP_KEY_FILENAME=dummy_sftp_private_key PUBSUB_EMULATOR_HOST=localhost:8538 pipenv run python run.py --log_level WARN
