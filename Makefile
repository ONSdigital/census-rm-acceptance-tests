install:
	pipenv install --dev

test:
	pipenv run behave acceptance_tests/features
