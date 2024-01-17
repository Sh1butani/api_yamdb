### Описание:
Проект предназначен для взаимодействия API для социальной сети YaMDb.
YaMDb собирает отзывы пользователей на различные произведения.

- Возможность просмотра, создания, редактирования и удаления отзывов.
- Просмотр произведений, категорий и жанров произведений.
- Возможность добавления, редактирования и удаления комментариев.
- Управление пользователями.
- Для аутентификации используются JWT-токены.

### Технологии:

**Языки программирования, библиотеки и модули:**

[![Python](https://img.shields.io/badge/Python-3.9.10%20-blue?logo=python)](https://www.python.org/)

**Фреймворк, расширения и библиотеки:**

[![Django](https://img.shields.io/badge/Django-v3.2.16-blue?logo=Django)](https://www.djangoproject.com/)


**Базы данных и инструменты работы с БД:**

[![SQLite3](https://img.shields.io/badge/-SQLite3-464646?logo=SQLite)](https://www.sqlite.com/version3.html)

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Sh1butani/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Примеры запросов к API:

Получение данных своей учетной записи:
GET /api/v1/users/me/

Частичное обновление информации о произведении:
PATCH /api/v1/titles/{titles_id}

Получение списка всех отзывов:
GET /api/v1/titles/{title_id}/reviews/

Добавление комментария к отзыву:
POST /api/v1/titles/{title_id}/reviews/{review_id}/comments/


Полный перечень запросов вы можете найти в документации к API, доступной после запуска сервера
по адресу: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/) 