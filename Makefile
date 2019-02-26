install:
	pipenv install --dev

acceptance_sequential_tests:
	pipenv run python run_in_sequence.py --log_level WARNING

acceptance_parallel_tests:
	pipenv run python run_in_parallel.py --log_level INFO
