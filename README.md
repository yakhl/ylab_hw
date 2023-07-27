# Меню ресторана
Меню ресторана на `FastAPI` с использованием `PostgreSQL` в качестве БД

## Зависимости
`Python3.10+` должен быть уже установлен. Затем используйте `pip` для установки зависимостей:

```bash
pip install -r requirements.txt
```

## Переменные окружения
Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` рядом с `main.py` и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`

Для запуска проекта **нужно указать** следущие переменные:
- **DB_USER** - имя пользователя
- **DB_PASS** - пароль 
- **DB_HOST** - хост БД
- **DB_PORT** - порт БД
- **DB_NAME** - имя БД

Например, если вы распечатаете содержимое `.env`, то увидите:

```bash
$ cat .env
DB_USER=postgres
DB_PASS=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=db
```

## Как запустить
Сначала примените миграции:
```bash
$ alembic upgrade head
```
Вы увидите:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> ce4c71971744, Initial
```

Запуск:
```bash
$ uvicorn main:app
```
Вы увидите:
```ы
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```
