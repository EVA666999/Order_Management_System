# FastAPI Order Management System

Это API сервис для управления заказами с возможностями аутентификации, асинхронной обработки задач и распределенного взаимодействия между сервисами.

## Основные возможности

- Регистрация и аутентификация пользователей с JWT токенами
- Создание и управление заказами
- Ограничение запросов (Rate Limiting)
- Кэширование через Redis
- Асинхронная обработка заказов через Celery
- Событийное взаимодействие через Kafka

## Технологии

- FastAPI
- PostgreSQL
- Redis
- Kafka
- Celery
- Docker и Docker Compose

## Установка и запуск

1. Клонируйте репозиторий:

```bash
git clone https://github.com/EVA666999/Order_Management_System
```

2. Создайте файл `.env` в корневой директории проекта:

```bash

POSTGRES_USER_local=your_postgres_user
POSTGRES_PASSWORD_local=your_password
POSTGRES_DB_local=your_postgresdb
DB_HOST_local=postgres
DB_PORT_local=5432
Для генерации SECRET_KEY используйте
import secrets
secret_key = secrets.token_hex(32)
print(secret_key)
SECRET_KEY=your_secret_key_here
```

3. Запустите приложение с помощью Docker Compose:

```bash
docker-compose up -d
```

4. Проверьте, что все сервисы запущены:

```bash
docker-compose ps
```

Приложение будет доступно по адресу: http://localhost:8000

Swagger UI документация: http://localhost:8000/docs
