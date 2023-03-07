# Продуктовый помощник
![example workflow](https://github.com/romaleg07/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
[![Python](https://img.shields.io/badge/-Python-464641?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)

[Foodgram](http://158.160.27.117/) - Мой проектик
админка: [Foodgram](http://158.160.27.117/amin)
логин: romaleg.sky@yandex.ru
пароль: qwerty

Foodgram это сервис для добавления рецептов, подписи на авторов, создания списков ингредиентов и фильтрацией по тегам.
Реализованы: регистрация и аутентификация по JWT токенам, добавление рецептов, привязка ингредиентов и тэгов для них. Добавление рецептов в изабранное и в корзину, откуда можно скачать списокм все нужные ингредиенты. Так же подписка на авторов и все его рецепты.
Все упаковано в Docker
Для фронтенда использован React.js

**Технологии:** Django, Django REST Framework, JWT, Docker, PosgreSQL, Docker-compose, Nginx, Gunicorn

## Технологии:
- [Django](https://www.djangoproject.com/) - Мощный framework для Python!
- [Django REST Framework](https://www.django-rest-framework.org) - мощный и гибкий инструмент для создания Web APIs
- [JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/) - JSON-токен для аутентификации.
- [Docker](https://www.docker.com) - интструмент для автоматизации развертывания приложений
- [Docker-compose](https://docs.docker.com/compose/) - приложение для развертывания нескольких контейнеров
- [PosgreSQL](https://www.postgresql.org) - база данных
- [Nginx](https://nginx.org/) - HTTP-сервер для статических данных
- [Gunicorn](https://gunicorn.org) - HTTP-сервер для динамических данных Django

## Установка

### Версии стека
Подробнее в requirements.txt
```
Python 3.10
Django 4.1.5
Django REST Framework 3.14.0
PyJWT 2.6.0
``` 

### Деплой
Установить и настроить докер.

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/romaleg07/foodgram-project-react.git
``` 
Установить на ваш сервер Docker и Docker-Compose 
Скопировать на ваш сервер папку infra
1) Открыть проект
2) Добавить ваш ip в файл infra/default.conf в раздел server_name
3) Выполнить команду 
```
$ scp -r infra username@host:/home/username
``` 
user - имя пользователя для вашего сервера
host - ip или домен вашего хостинга

4) Забилдить и поднять проект:
```
$ docker-compose up -d --build 
``` 
После развертывания проекта нужно выполнить миграции в папке ingra:
```
docker-compose exec backend python manage.py migrate
```
Создать суперюзера:
```
$ docker-compose exec backend python manage.py createsuperuser
```
Собрать статику для сайта:
```
$ docker-compose exec backend python manage.py collectstatic --no-input
```
Импортировать ингредиенты и тэги:
```
$ docker-compose exec backend python manage.py load_ingredients
$ docker-compose exec backend python manage.py load_tags
```


## Проект развернут!
