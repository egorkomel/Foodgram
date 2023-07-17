# Foodgram - продуктовый помощник
![foodgram workflow](https://github.com/egorkomel/foodgram-project-react/actions/workflows/foodgram-workflow.yml/badge.svg)

Foodgram - это сервис, на котором можно публиковать рецепты. Возможность размещать свои рецепты появляется после регистрации. А еще появляется возможность подписываться на других пользователей, добавлять рецепты в избранное и список покупок. При создании рецепта указываются теги и ингредиенты. Благодаря тегам, можно отфильтровать интересующие рецепты. А список покупок формируется из ингредиентов в рецептах, которые лежат в списке покупок.

Проект собран на пяти контейнерах Docker через docker-compose:
 - db: postgres:13.0;
 - backend: egorkomel/foodgram-api;
 - frontend: egorkomel/foodgram-frontend;
 - nginx: nginx:1.21.3;
 - certbot: certbot/certbot;

Также в проекте настроен CI/CD. Рабочий процесс (workflow) описан в файле foodgram-workflow.yml и добавлен в директорию foodgram-project-react/.github/workflows. В файле описано три действия. При push в main:
- tests - запуск тестов на соответствие кода PEP8;
- Push Docker image to Docker Hub - сборка актуальной версии Docker образа и push на DockerHub (контейнер backend);
- deploy - деплой на боевой сервер;


### Технологии
В проекте использованы ниже перечисленные технологии:
- Python 3.7
- Django 3.2
- djangorestframework 3.12.4
- PyJWT 2.1.0
- Docker 23.0.6
- docker-compose 1.29.2
- PostgreSQL 13.0
- NGINX 1.21.3
- gunicorn 20.1.0

### Установка
Ниже приведены команды для локального запуска проекта для Linux сиcтем.
Предварительно необходимо установить у себя Docker и docker-compose.

Первым делом установим утилиту для скачивания файлов:
```
apt install curl
```
Скачиваем скрипт для установки Docker и запускаем его:
```
curl -fsSL https://get.docker.com -o get-docker.sh
```
```
sh get-docker.sh   
```
Устанавливаем docker-compose:
```
apt update
```
```
apt install docker-ce
```

Клонируем репозиторий:
```
git clone https://github.com/egorkomel/foodgram-project-react/
```

Переходим в директорию с файлом docker-compose.yaml:
```
cd foodgram-project-react/infra
```

Запускам контейнеры Docker с помощью команды:
```
sudo docker-compose up -d --build
```

При успешном запуске в консоли должны быть выведены строки:
```
Creating infra-frontend-1  ... done
Creating infra-db-1 ... done
Creating infra-backend-1 ... done
Creating infra-nginx_1 ... done
Creating nfra-certbot-1   ... done
```

Для автоматизации написан скрипт manage_commands.sh, в котором выполняются команды миграций, сбора статики и наполнение БД ингредиентами. Для выполнения скрипта пишем в консоли команду:
```
docker compose exec backend bash manage_commands.sh
```
Теперь создаем суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```
После этого документация redoc доступна по адресу:
```
http://localhost/api/docs/
```
Вход для суперпользователя доступен по адресу:
```
http://localhost/admin/
```

### Разработчики:
Егор Комелягин (egorkomel@gmail.com)
