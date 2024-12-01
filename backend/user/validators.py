import re

from django.core.exceptions import ValidationError

from api.constants import REGEX_VALIDATION


def validate_username(value):
    if value == "me":
        raise ValidationError("Недопустимое имя")
    elif value in re.sub(REGEX_VALIDATION, "", value):
        raise ValidationError("Недопустимые символы")
