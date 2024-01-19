import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import (Category, Comment, Genre, Review,
                            Title, User, TitleGenre)


class Command(BaseCommand):
    help = 'Загрузка csv файлов в базу данных'

    def ImportUser(self):
        if User.objects.exists():
            print('Данные для User уже загружены.')
        else:
            with open(
                settings.BASE_DIR / 'static/data/users.csv',
                'r',
                encoding='utf8'
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    User.objects.create(
                        id=row['id'],
                        username=row['username'],
                        email=row['email'],
                        role=row['role'],
                        bio=row['bio'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],)
                print('Данные для User успешно загружены!')

    def ImportGenre(self):
        if Genre.objects.exists():
            print('Данные для Genre уже загружены.')
        else:
            with open(
                settings.BASE_DIR / 'static/data/genre.csv',
                'r',
                encoding='utf8'
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Genre.objects.create(
                        id=row['id'],
                        name=row['name'],
                        slug=row['slug'],)
                print('Данные для Genre успешно загружены!')

    def ImportCategory(self):
        if Category.objects.exists():
            print('Данные для Category уже загружены.')
        else:
            with open(
                settings.BASE_DIR / 'static/data/category.csv',
                'r',
                encoding='utf8'
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Category.objects.create(
                        id=row['id'],
                        name=row['name'],
                        slug=row['slug'],)
                print('Данные для Category успешно загружены!')

    def ImportTitle(self):
        if Title.objects.exists():
            print('Данные для Title уже загружены.')
        else:
            with open(
                settings.BASE_DIR / 'static/data/titles.csv',
                'r',
                encoding='utf8'
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Title.objects.create(
                        id=row['id'],
                        name=row['name'],
                        year=row['year'],
                        category=Category.objects.get(id=row['category']),)
                print('Данные для Title успешно загружены!')

    def ImportGenreTitle(self):
        if TitleGenre.objects.exists():
            print('Данные для TitleGenre уже загружены.')
        else:
            with open(
                settings.BASE_DIR / 'static/data/genre_title.csv',
                'r',
                encoding='utf8'
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    TitleGenre.objects.create(
                        id=row['id'],
                        title_id=row['title_id'],
                        genre_id=row['genre_id'],)
                print('Данные для TitleGenre успешно загружены!')

    def ImportReview(self):
        if Review.objects.exists():
            print('Данные для Review уже загружены.')
        else:
            with open(
                settings.BASE_DIR / 'static/data/review.csv',
                'r',
                encoding='utf8'
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Review.objects.create(
                        id=row['id'],
                        title_id=row['title_id'],
                        text=row['text'],
                        author=User.objects.get(id=row['author']),
                        score=row['score'],
                        pub_date=row['pub_date'],)
                print('Данные для Review успешно загружены!')

    def ImportComments(self):
        if Comment.objects.exists():
            print('Данные для Comment уже загружены.')
        else:
            with open(
                settings.BASE_DIR / 'static/data/comments.csv',
                'r',
                encoding='utf8'
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Comment.objects.create(
                        id=row['id'],
                        review_id=row['review_id'],
                        text=row['text'],
                        author=User.objects.get(id=row['author']),
                        pub_date=row['pub_date'],)
                print('Данные для Comment успешно загружены!')

    def handle(self, *args, **kwargs):
        self.ImportUser()
        self.ImportGenre()
        self.ImportCategory()
        self.ImportTitle()
        self.ImportGenreTitle()
        self.ImportReview()
        self.ImportComments()
