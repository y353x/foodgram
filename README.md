Сайт под названием «Фудграм», где пользователи могут публиковать свои рецепты, добавлять понравившиеся рецепты других пользователей в избранное и подписываться на публикации авторов. Для зарегистрированных пользователей доступен сервис «Список покупок», который позволит создавать перечень продуктов, необходимых для приготовления выбранных блюд.
Для каждого рецепта можно получить прямую короткую ссылку, нажав на соответствующую иконку справа от названия рецепта. 

## Запуск проекта ##

- склонировать репозиторий
    - git clone git@github.com:y353x/foodgram.git
- создать файл .env в папке infra
    - пример файла в *env.example*
- запустить сборку контейнера в Docker
    - для локального размещения:
        - *docker compose -f docker-compose.yml up -d --build*
    - для размещения на сервере:
        - *sudo docker compose -f docker-compose.production.yml up -d*
- произвести миграции
    - для локального размещения:
        - *docker compose -f docker-compose.yml exec backend python manage.py migrate*
    - для размещения на сервере:
        - *sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate*
- собрать статику и скопировать на сервер:
    - для локального размещения:
        - *docker compose -f docker-compose.yml exec backend python manage.py collectstatic*
        - *docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/*
    - для размещения на сервере:
        - *sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic*
        - *sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/*
- наполнить БД ингредиентами
    - для локального размещения:
        - *docker compose -f docker-compose.yml exec backend python manage.py import_json*
    - для размещения на сервере:
        - *sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_json*

- Эндпоинты
    - /api/users/ + /me/ + /me/avatar/ + /set_password/ + /subscriptions/
    - /api/users/{id}/ + /subscribe/
    - /api/auth/token/ + /login/ + /logout/
    - /api/tags/ + /{id}/
    - /api/ingredients/ + /{id}/
    - /api/recipes/ + /download_shopping_cart/
    - /api/recipes/{id}/ + /shopping_cart/ + /favorite/ + /get-link/


Технологи

- Python 3.9.13
- Django 4.2.16
- Django Rest Framework 3.15.2
- Authtoken
- Docker
- Docker-compose
- PostgreSQL
- Gunicorn
- Nginx
- GitHub Actions


#### [Развернутый проект в сети](https://ruspraktikum.hopto.org/) ####
#### [Документация к API (redoc)](https://ruspraktikum.hopto.org/api/docs/) ####
![example workflow](https://github.com/y353x/foodgram/actions/workflows/main.yml/badge.svg)
##### Автор: Селимов Р.С. #####

