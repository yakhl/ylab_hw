# Меню ресторана
Меню ресторана на `FastAPI` с использованием `PostgreSQL` в качестве БД

## Запуск через `Docker`
[Docker](https://www.docker.com/) должен быть установлен

### Переменные окружения
Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` в корне проекта и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`

Для запуска проекта **обазательно нужно указать** следущие переменные:
- **POSTGRES_DB** - название БД
- **POSTGRES_USER** - имя пользователя БД 
- **POSTGRES_PASSWORD** - пароль БД

Опциональные переменные:
- **LOCAL_POSTGRES_PORT** - порт для БД на вашей машине(по-умолчанию: 5432)
- **LOCAL_FASTAPI_PORT** - порт для API на вашей машине(по-умолчанию: 80)

Внутри контейнеров установлены следующие порты:
- **5432** - для БД
- **80** - для API

Файл `.env` может выглядить примерно так:

```bash
$ cat .env
POSTGRES_DB=postgres_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234
LOCAL_POSTGRES_PORT=6789
LOCAL_FASTAPI_PORT=8080
```

### Запуск
Запустите `Docker` и введите команду, находясь в корне проекта:
```bash
$ docker-compose up -d
```

Вы увидите:
```bash
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
```bash
==================== test session starts ====================
platform linux -- Python 3.10.12, pytest-7.4.0, pluggy-1.2.0
rootdir: /code
plugins: anyio-3.7.1
collected 36 items

tests/test_dishes.py ............... [ 41%]
tests/test_menus.py .........        [ 66%]
tests/test_submenus.py ............  [100%]

==================== 36 passed in 1.78s ====================
```

Запустить контейнер с тестами можно повторно:
```bash
$ docker start -a tests_ylab
```

Но сначала запустите контейнеры с БД и API.
