from django.core.exceptions import ValidationError
from django.utils.timezone import now


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.'),
            params={'value': value},
        )


def year_validator(value):
    """Валидатор вводимого года."""
    current_year = now().year
    if value > current_year:
        raise ValidationError('Год не может быть позже текущего года.')
    return value
