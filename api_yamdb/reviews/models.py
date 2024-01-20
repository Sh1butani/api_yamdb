from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.settings import (
    ADMIN,
    MAX_LENGTH,
    MAX_MARK,
    MAX_NAME_LENGTH,
    MAX_ROLE_LENGTH,
    MIN_MARK,
    MODERATOR,
    USER,
)

from .validators import validate_username, year_validator


class User(AbstractUser):
    """Кастомная модель пользователя"""
    ROLES = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin')
    ]
    username = models.CharField(
        'Имя пользователя',
        unique=True,
        max_length=MAX_LENGTH,
        validators=[UnicodeUsernameValidator(), validate_username]
    )

    email = models.EmailField(unique=True,
                              verbose_name='Почта')
    first_name = models.CharField(
        'Имя', max_length=MAX_LENGTH, blank=True
    )
    last_name = models.CharField(
        'Фамилия', max_length=MAX_LENGTH, blank=True
    )
    bio = models.TextField(
        'Биография', blank=True
    )
    role = models.CharField(
        'Роль',
        choices=ROLES,
        default=USER,
        max_length=MAX_ROLE_LENGTH,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    @property
    def is_admin(self):
        """Проверяем является ли пользователь админом или суперюзером"""
        return (
            self.role == ADMIN
            or self.is_superuser
            or self.is_staff
        )

    @property
    def is_moderator(self):
        """Проверяем является ли пользователь модератором"""
        return self.role == MODERATOR

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            verbose_name='Название')
    slug = models.SlugField(unique=True,
                            verbose_name='Уникальный слаг')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            verbose_name='Название')
    slug = models.SlugField(unique=True,
                            verbose_name='Уникальный слаг')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


class Title(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='title'
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
        verbose_name='Жанр'
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name='Название'
    )
    year = models.SmallIntegerField(
        'Год выпуска',
        validators=(year_validator,),
        help_text='Введите год, который не превышает текущий.',)
    description = models.TextField(
        verbose_name='Описание', blank=True,
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']

    def __str__(self):
        return self.name


class TitleGenre(models.Model):

    title = models.ForeignKey(
        Title,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Жанр',
    )

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f'{self.title} - {self.genre}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=(
            MinValueValidator(
                MIN_MARK,
                message=f'Нельзя ставить оценку ниже {MIN_MARK}.',
            ),
            MaxValueValidator(
                MAX_MARK,
                message=f'Нельзя ставить оценку выше {MAX_MARK}.',
            ),
        ),
        help_text=f'Введите оценку от {MIN_MARK} до {MAX_MARK}.'
    )
    text = models.TextField(
        verbose_name='Отзыв'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_unique_review',
                fields=['author', 'title'],
            ),
        ]
        ordering = ('pub_date',)

    def __str__(self):
        return f'{self.author} оставил отзыв на {self.title}'


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Комментарий'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date',)

    def __str__(self):
        return f'Комментарий на {self.review} от {self.author}'
