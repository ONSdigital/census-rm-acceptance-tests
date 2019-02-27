import string
from random import choice, randint


def create_random_string(min_len, max_len):
    random_chars = string.ascii_uppercase + string.digits
    return "".join(choice(random_chars) for _ in range(randint(min_len, max_len)))
