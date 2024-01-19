from django.core.exceptions import ValidationError
from django.utils.timezone import now


def validate_username(value):
    """Запрещает использовать 'me' в качестве имени."""
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.'),
            params={'value': value},
        )


def year_validator(value):
    """Запрещает использовать года позже текущего."""
    current_year = now().year
    if value > current_year:
        raise ValidationError('Год не может быть позже текущего года.')
    return value
