install:
	pipenv install --dev

package_vulnerability:
	pipenv check

flake:
	pipenv run flake8 .

test: package_vulnerability flake set_pubsub_emulator at_tests

set_pubsub_emulator:
	./set_pubsub_emulator.sh

at_tests:
	pipenv run python run.py --log_level WARN
