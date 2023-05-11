![django-app workflow](https://github.com/bobhawler/foodgram-project/actions/workflows/main.yml/badge.svg)        [![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/-JWT-464646?style=flat&color=008080)](https://jwt.io/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=56C0C0&color=008080)](https://cloud.yandex.ru/)

# Foodgram
Сервис позволяет создавать рецепты, подписываться на интересных авторов, добавлять понравившиеся блюда в избранное и в список покупок, откуда можно в один клик скачать список нужных ингредиетов.

### Страница проекта:
http://84.201.176.137

## Как запустить проект:

### Установите на сервере Docker и docker-compose:
```
sudo apt install docker.io
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
### Скопируйте на сервер файлы docker-compose.yml и nginx.conf:
```
scp docker-compose.yml <логин_на_сервере>@<ip_сервера>:/home/<логин_на_сервере>/docker-compose.yml
scp nginx.conf <логин_на_сервере>@<ip_сервера>:/home/<логин_на_сервере>/nginx/nginx.conf
```
### В репозитории на Гитхабе добавьте данные в Settings - Secrets - Actions secrets:
```
DOCKER_USERNAME - имя пользователя в DockerHub
DOCKER_PASSWORD - пароль пользователя в DockerHub
HOST - ip-адрес сервера
USER - пользователь
SSH_KEY - приватный ssh-ключ (публичный должен быть на сервере)
PASSPHRASE - кодовая фраза для ssh-ключа
DB_ENGINE - django.db.backends.postgresql
DB_HOST - db
DB_PORT - 5432
SECRET_KEY - секретный ключ приложения django (необходимо чтобы были экранированы или отсутствовали скобки)
ALLOWED_HOSTS - список разрешённых адресов
TELEGRAM_TO - id своего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN - токен бота (получить токен можно у @BotFather, /token, имя бота)
DB_NAME - postgres (по умолчанию)
POSTGRES_USER - postgres (по умолчанию)
POSTGRES_PASSWORD - postgres (по умолчанию)
```
## После успешного деплоя:

### Примените миграции:
```
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate --noinput
```
### Создайте суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```
### Загрузите список ингредиентов:
```
docker-compose exec web python manage.py load_ingredients
```
### Загрузите список тегов:
```
docker-compose exec web python manage.py load_tags
```
### Доступны следующие эндпоинты:
```
/api/users/ - список пользователей;
/api/users/{id} - страница пользователя по id;
/api/users/me/ - страница текущего пользователя;
/api/users/set_password - изменение пароля;
/api/auth/token/login/ - получение токена; 
/api/auth/token/logout/ - удаление токена;
/api/tags/ - получение списка всех тегов;
/api/tags/{id} информация о теге;
/api/ingredients/ - список ингредиентов;
/api/ingredients/{id}/ - информация об ингредиенте;
/api/recipes/ - список рецептов;
/api/recipes/{id}/ информация о рецепте;
/api/recipes/?is_favorited=1 - избранные рецепты;
/api/recipes/is_in_shopping_cart=1 - список покупок;
/api/recipes/{id}/favorite/ - добавление рецепта визбранное;
/api/recipes/{id}/shopping_cart/ - добавление рецепта в список покупок;
/api/recipes/download_shopping_cart/ - получение списка покупок;
/api/users/{id}/subscribe/ - подписка на пользователя;
/api/users/subscriptions/ - список пользователей, на которых подписан текущий пользователь.
```
### Разработчик:
 Anatoly Konovalov (BobHawler)
