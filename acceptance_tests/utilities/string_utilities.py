import string
from random import choice, randint, random


def random_string_upper_or_digits(min_len, max_len):
    random_chars = string.ascii_uppercase + string.digits
    return "".join(choice(random_chars) for _ in range(randint(min_len, max_len)))


def create_random_postcode():
    return (f'{random_string_upper_or_digits(3, 4)}'
            f'{" " if random() > 0.5 else ""}'
            f'{choice(string.digits)}'
            f'{choice(string.ascii_uppercase)}'
            f'{choice(string.ascii_uppercase)}')
