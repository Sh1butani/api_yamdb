import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import (Category, Comment, Genre, Review,
                            Title, User, TitleGenre)


DATABASE = {
    Category: 'category.csv',
    Comment: 'comments.csv',
    Genre: 'genre.csv',
    TitleGenre: 'title_genre.csv',
    Review: 'review.csv',
    Title: 'titles.csv',
    User: 'users.csv'
}


class Command(BaseCommand):
    help = 'Загрузка csv файлов в базу данных'

    def handle(self, *args, **kwargs):
        for model, csv_file in DATABASE.items():
            if model.objects.exists():
                print('База данных существует')
                return

            with open(
                    f'{settings.BASE_DIR}/static/data/{csv_file}',
                    'r',
                    encoding='utf-8',
            ) as file:
                reader = csv.DictReader(file)
                for data in reader:
                    model.objects.get_or_create(**data)
        self.stdout.write(self.style.SUCCESS('Данные успешно загружены!'))
