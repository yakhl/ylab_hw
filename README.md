# Меню ресторана
Меню ресторана на `FastAPI` с использованием `PostgreSQL` в качестве БД и `Redis` для кеширования

## Запуск через `Docker`
[Docker](https://www.docker.com/) должен быть установлен

### Переменные окружения
Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` в корне проекта и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`

Для запуска проекта **обязательно нужно указать** следующие переменные:
- **POSTGRES_DB** - название БД
- **POSTGRES_USER** - имя пользователя БД
- **POSTGRES_PASSWORD** - пароль БД

Опциональные переменные:
- **LOCAL_POSTGRES_PORT** - порт для БД на вашей машине (по-умолчанию: 5432)
- **LOCAL_FASTAPI_PORT** - порт для API на вашей машине (по-умолчанию: 80)
- **LOCAL_REDIS_PORT** - порт для Redis на вашей машине (по-умолчанию: 6379)

Внутри контейнеров установлены следующие порты:
- **5432** - для БД
- **80** - для API
- **6379** - для Redis

Файл `.env` может выглядеть примерно так:

```
POSTGRES_DB=postgres_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234
LOCAL_POSTGRES_PORT=6789
LOCAL_FASTAPI_PORT=8080
LOCAL_REDIS_PORT=6380
```

### Как запустить
Запустите `Docker` и введите команду, находясь в корне проекта:

```bash
$ docker-compose up -d
```

Вы увидите:

```
[+] Running 3/3
 ✔ Container postgres_ylab  Healthy
 ✔ Container fastapi_ylab   Healthy
 ✔ Container tests_ylab     Started
```

Чтобы посмотреть логи тестов после их завершения выполните команду:

```bash
$ docker logs tests_ylab
```

Вы увидите:

```
==================== test session starts ====================
platform linux -- Python 3.10.12, pytest-7.4.0, pluggy-1.2.0
rootdir: /code
plugins: anyio-3.7.1
collected 39 items

tests/test_dishes.py ...............                   [ 41%]
tests/test_menus.py .........                          [ 66%]
tests/test_submenus.py ............                    [100%]
==================== 39 passed in 1.78s =====================
```

Запустить контейнер с тестами можно отдельно:

```bash
$ docker start -a tests_ylab
```

Но сначала запустите контейнеры с БД, Redis и API.
Перед запуском тестов убедитесь, что БД пуста.
Тесты могут работать без Redis, но медленно


## Запуск `локально`
Используйте виртуальное окружение и [Python3.10+](https://www.python.org/downloads/)

### Зависимости
Установите зависимости:

```bash
pip install -r ./core_requirements.txt -r ./tests_requirements.txt
```

Основные зависимости: `core_requirements.txt`
Зависимости для тестирования: `tests_requirements.txt`

### Переменные окружения
Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` в корне проекта и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`

Для запуска проекта можно указать следующие переменные:
- **POSTGRES_DB** - название БД (по-умолчанию: postgres_db)
- **POSTGRES_USER** - имя пользователя БД (по-умолчанию: postgres)
- **POSTGRES_PASSWORD** - пароль БД (по-умолчанию: 1234)
- **POSTGRES_HOST** - хост БД (по-умолчанию: localhost)
- **POSTGRES_PORT** - порт БД (по-умолчанию: 5432)
- **REDIS_HOST** - хост Redis (по-умолчанию: localhost)
- **REDIS_PORT** - порт Redis (по-умолчанию: 6379)
- **FASTAPI_HOST** - хост API для тестов (по-умолчанию: localhost)
- **FASTAPI_PORT** - порт API для тестов (по-умолчанию: 8000)

Файл `.env` может выглядеть примерно так:

```
POSTGRES_DB=mydb
POSTGRES_USER=myusername
POSTGRES_PASSWORD=4321
```

### Как запустить
Примените миграции:

```bash
$ alembic upgrade head
```

Вы увидите:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 3c6dc4af3e35, initial
```

Запустите сервер:

```bash
$ uvicorn core.main:app
```

Вы увидите:
```
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Запустите тесты:

```bash
$ pytest
```

Вы увидите:
```
==================== test session starts ====================
platform linux -- Python 3.10.12, pytest-7.4.0, pluggy-1.2.0
rootdir: /code
plugins: anyio-3.7.1
collected 39 items

tests/test_dishes.py ...............                   [ 41%]
tests/test_menus.py .........                          [ 66%]
tests/test_submenus.py ............                    [100%]
==================== 39 passed in 1.78s =====================
```
