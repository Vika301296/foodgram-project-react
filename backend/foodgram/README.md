# Foodrgam

 Продуктовый помощник - дипломный проект курса Backend-разработки Яндекс.Практикум. Проект представляет собой онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект реализован на `Django` и `DjangoRestFramework`. Доступ к данным реализован через API-интерфейс. Документация к API написана с использованием `Redoc`.

# Стек технологий

* Python
* Django REST API
* библиотека Simple JWT - работа с JWT-токеном
* Postgres
* Docker

### Как запустить проект:
- Склонируйте репозитрий на свой компьютер

- Создайте `.env` файл в директории `infra/`, в котором должны содержаться следующие переменные:
    >DB_ENGINE=django.db.backends.postgresql\
    >DB_NAME= # название БД\ 
    >POSTGRES_USER= # ваше имя пользователя\
    >POSTGRES_PASSWORD= # пароль для доступа к БД\
    >DB_HOST=db\
    >DB_PORT=5432\

- Установите docker-compose на сервер:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

- Запустите docker-compose:
```
docker-compose up -d --build
```

- Соберите файлы статики, и запустите миграции командами:
```
docker-compose exec web python3 manage.py makemigrations
```
```
docker-compose exec web python3 manage.py migrate
```
```
docker-compose exec web python3 manage.py collectstatic --no-input
```

- Заполните БД ингредиентами
```
docker-compose exec web python3 manage.py load_inhredients
```

- Создайте суперпользователя командой:
```
docker-compose exec web python3 manage.py createsuperuser
```

- Остановить можно командой:
```
docker-compose down -v
```

### Ресурсы Foodgram

* Ресурс USERS: пользователи.
* Ресурс TAGS: тэги.
* Ресурс RECIPIES: рецепты.
* Ресурс SHOPPING_CART: окрзина покупок.
* Ресурс FAVORITE: избранное.
* Ресурс SUBSCRIPTIONS: подписки.
* Ресурс INGREDIENTS: ингредиенты.

Каждый ресурс описан в документации: указаны эндпойнты (адреса, по которым можно сделать запрос), разрешённые типы запросов, права доступа и дополнительные параметры, если это необходимо.

### Развернутый проект:
http://158.160.24.209/

## Автор
Федорова Виктория (https://github.com/vika301296)
![foodgram-project-react](https://github.com/vika301296/foodgram-project-react/actions/workflows/foodgram-project-react.yml/badge.svg)