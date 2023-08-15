##### ***Задания со звездочкой:***

- ###### ***Тесты для проверки количества блюд и подменю – [test_counters.py](https://github.com/yakhl/ylab_hw/blob/main/tests/test_counters.py)***

- ###### ***Подсчет количества подменю и блюд для меню через один ORM запрос – [menu_repository.py #L20](https://github.com/yakhl/ylab_hw/blob/main/core/repositories/crud/menu_repository.py#L20)***
___

# Меню ресторана
Меню ресторана на `FastAPI` с использованием `PostgreSQL` в качестве БД и `Redis` для кеширования.

С помощь `Celery` и `RabbitMQ` каждые 15 секунд в БД обновляются данные в соответствии с таблицей ***Menu.xlsx***

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
- **LOCAL_RABBIT_PORT** - порт для RabbitMQ на вашей машине (по-умолчанию: 5672)
- **LOCAL_RABBIT_GUI_PORT** - порт для GUI RabbitMQ на вашей машине (по-умолчанию: 15672)

Внутри контейнеров установлены следующие порты:
- **5432** - для БД
- **80** - для API
- **6379** - для Redis
- **5672** - для RabbitMQ
- **15672** - для GUI RabbitMQ

Файл `.env` может выглядеть примерно так:

```
POSTGRES_DB=postgres_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234
LOCAL_POSTGRES_PORT=6789
LOCAL_FASTAPI_PORT=8080
LOCAL_REDIS_PORT=6380
LOCAL_RABBIT_PORT=5670
```

### Как запустить
Запустите `Docker` и введите команду, находясь в корне проекта:

```bash
$ docker-compose up -d
```

Вы увидите:

```
[+] Running 6/6
 ✔ Container postgres_ylab       Healthy
 ✔ Container redis_ylab          Healthy
 ✔ Container rabbitmq_ylab       Healthy
 ✔ Container fastapi_ylab        Healthy
 ✔ Container celery_beat_ylab    Started
 ✔ Container celery_worker_ylab  Started
```

Для запуска тестов API с отдельными БД и Redis используйте:

```bash
$ docker-compose -f docker-compose.test.yml up -d
```

Вы увидите:

```
[+] Running 3/3
 ✔ Container postgres_test  Healthy
 ✔ Container redis_test     Healthy
 ✔ Container fastapi_test   Started
```

Чтобы посмотреть логи тестов после их завершения введите:

```bash
$ docker logs fastapi_test
```

Вы увидите:

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 4db770efe029, initial
==================== test session starts ====================
platform linux -- Python 3.10.12, pytest-7.4.0, pluggy-1.2.0
rootdir: /code
plugins: anyio-3.7.1, asyncio-0.21.1
asyncio: mode=strict
collected 46 items

tests/test_dishes.py ...............                   [ 34%]
tests/test_full_menu.py .......                        [ 50%]
tests/test_menus.py .........                          [ 71%]
tests/test_submenus.py ............                    [100%]
==================== 46 passed in 1.78s =====================
```

## Запуск `локально`
Используйте виртуальное окружение и [Python3.10+](https://www.python.org/downloads/)
Для работы Celery должен быть запущен [RabbitMQ](https://www.rabbitmq.com/)

### Зависимости
Установите зависимости:

```bash
pip install -r requirements.txt -r celery_app/celery_requirements.txt
```

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
- **FASTAPI_HOST** - хост API для Celery (по-умолчанию: localhost)
- **FASTAPI_PORT** - порт API для Celery (по-умолчанию: 8000)
- **RABBIT_HOST** - хост RabbitMQ для Celery (по-умолчанию: localhost)
- **RABBIT_PORT** - порт RabbitMQ для Celery (по-умолчанию: 5672)

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
INFO  [alembic.runtime.migration] Running upgrade  -> 4db770efe029, initial
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
$ pytest -p no:warnings
```

Вы увидите:
```
==================== test session starts ====================
platform linux -- Python 3.10.12, pytest-7.4.0, pluggy-1.2.0
rootdir: /code
plugins: anyio-3.7.1, asyncio-0.21.1
asyncio: mode=strict
collected 46 items

tests/test_dishes.py ...............                   [ 34%]
tests/test_full_menu.py .......                        [ 50%]
tests/test_menus.py .........                          [ 71%]
tests/test_submenus.py ............                    [100%]
==================== 46 passed in 1.78s =====================
```

Запустите Celery worker:

```bash
celery -A celery_app.tasks worker --loglevel=INFO --pool=solo
```

Вы увидите:
```
...
mingle: searching for neighbors
mingle: all alone
celery@PC ready.
...
Task celery_app.tasks.sync_table[...] succeeded in 2.0s
...
```

Запустите Celery beat:

```bash
celery -A celery_app.tasks beat --loglevel=INFO
```

Вы увидите:
```
celery beat v5.3.1 (emerald-rush) is starting.
...
beat: Starting...
Scheduler: Sending due task sync-table-every-15-seconds (celery_app.tasks.sync_table)
...
```
