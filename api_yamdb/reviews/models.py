from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
MAX_LENGTH = 150
MAX_EMAIL_LENGTH = 254
MAX_TITLE_LENGTH = 20
MAX_NAME_LENGTH = 256
MAX_SLUG_LENGTH = 50


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
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='Недопустимый символ!'
        )]
    )

    email = models.EmailField(max_length=MAX_EMAIL_LENGTH,
                              unique=True,
                              verbose_name='Почта')
    first_name = models.CharField(
        'Имя', max_length=MAX_LENGTH, blank=True
    )
    last_name = models.CharField(
        'Фамилия', max_length=MAX_LENGTH, blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(
        'Роль',
        choices=ROLES,
        default=USER,
        max_length=25,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(username=models.F('me')),
                name="prevent_username_me"
            )
        ]

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

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:MAX_TITLE_LENGTH]


class Category(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            verbose_name='Название')
    slug = models.SlugField(max_length=MAX_SLUG_LENGTH,
                            unique=True,
                            verbose_name='Уникальный слаг')

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            verbose_name='Название')
    slug = models.SlugField(max_length=MAX_SLUG_LENGTH,
                            unique=True,
                            verbose_name='Уникальный слаг')

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
        verbose_name='Жанр',
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name='Название'
    )
    year = models.IntegerField(
        verbose_name='Год издания'
    )
    description = models.TextField(
        verbose_name='Описание', blank=True
    )

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
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка'
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
        unique_together = ('title', 'author',)

    def __str__(self):
        return f'{self.author} left review on {self.title}'


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

    def __str__(self):
        return f'Comment on {self.review} by {self.author}'
