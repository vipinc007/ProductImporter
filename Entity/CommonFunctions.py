import random
from flask import session


def generate_random_number():
    rand1 = random.randrange(10000, 5000000, 3)
    rand2 = random.randrange(10000, 5000000, 3)
    return str(rand1) + str(rand2)


def register_session(key, value):
    session[key] = value


def get_session_value(key):
    return session[key]


def check_session_key_exists(key):
    return key in session
