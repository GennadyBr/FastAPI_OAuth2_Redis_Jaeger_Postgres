# Сервис авторизации и аутентификации пользователей

Проект: https://github.com/KarinaSmirnova/Auth_sprint_1

Сервис предназначения для регистрации пользователей, хранения их аутентификационных данных, выдачи токенов доступа.

Помимо этого, сервис включает в себя управление ролями пользователей.

## Запуск

1. Скопировать файл .env.example и заполнить значениями;
1. Выполнить команду `docker compose up -d --build`;
1. Подготовьте БД командой: `docker-compose exec auth alembic upgrade head`;
1. Создайте суперпользователя: `docker-compose exec auth python create_superuser.py --name <admin name> --surname <admin surname> --login <admin login> --email <admin@example.com> --password <somepassword>`. 

В результате будут запущены: база данных пользователей, база данных для истекших токенов, сервис авторизации и аутентификации.

## Документация к API

После успешного запуска документация будет доступна по адресу: 

http://localhost:8081/api/openapi


## Тесты

1. Изменить файл .env.test;
2. Выполнить следующие команды:

```
cd tests
docker compose up -d --build
```
