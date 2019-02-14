import string
from random import choice, randint

RANDOM_CHARS = string.ascii_uppercase + string.digits

SURVEY_REFERENCE_MIN_LEN = 13
SURVEY_REFERENCE_MAX_LEN = 13


def create_survey_ref():
    survey_ref = create_random_string(SURVEY_REFERENCE_MIN_LEN, SURVEY_REFERENCE_MAX_LEN)

    return f'Census-{survey_ref}'


def create_random_string(min_len, max_len):
    return "".join(choice(RANDOM_CHARS) for x in range(randint(min_len, max_len)))
