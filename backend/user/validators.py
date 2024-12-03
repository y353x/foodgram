import re

from django.core.exceptions import ValidationError

from api.constants import ACTION_ME, REGEX_VALIDATION


def validate_username(value):
    if value == ACTION_ME:
        raise ValidationError('Недопустимое имя')
    if value in re.sub(REGEX_VALIDATION, '', value):
        raise ValidationError('Недопустимые символы')
    return value
