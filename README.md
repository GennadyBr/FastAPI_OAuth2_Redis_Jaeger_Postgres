# Сервис авторизации и аутентификации пользователей FastAPI, OAuth2, PostgreSQL, Redis, Jaeger

[Ссылка на проект](https://github.com/GennadyBr/FastAPI_OAuth2_Redis_Jaeger_Postgres)

**Сервис предназначения для регистрации пользователей, хранения их аутентификационных данных, выдачи токенов доступа**
- API реализована в FastAPI
- JWT токены хранятся в REDIS
- Сервис включает в себя управление ролями пользователей, которые хранятся в PostrgreSQL.
- реализована трассировка в Jaeger
- веб-сервер NGINX
- логирование с помощью logging
- линтер flake8
- .env и docker-compose.override.yml присутствуют в демонстрационных целях
- проект упакован в Docker Compose и запущен на VPS

## Проект уже запущен на сайте
## FastAPI
http://5.35.83.245/auth_api/openapi

## Jaeger
http://5.35.83.245:16686/search



## Запуск на локальной машине

1. git clone git@github.com:GennadyBr/FastAPI_OAuth2_Redis_Jaeger_Postgres.git
2. файл .env уже заполнен значениями;
2. Выполнить команду `docker compose up -d --build`;
3. Подготовьте БД командой: `docker compose exec auth_app alembic upgrade head`;
4. Создайте суперпользователя: `docker compose exec auth python create_superuser.py --name <admin name> --surname <admin surname> --login <admin login> --email <admin@example.com> --password <somepassword>`.
 
В результате будут запущены: база данных пользователей, база данных для истекших токенов, сервис авторизации и аутентификации.

## Документация к API

После успешного запуска документация будет доступна по адресу: 

http://localhost/auth_api/openapi


## Jaeger UI

После успешного запуска Jaeger UI будет доступен по адресу: 

http://localhost:16686/search


## Тесты

1. Изменить файл .env.test;
2. Выполнить следующие команды:

```
cd tests
docker compose up -d --build
```
