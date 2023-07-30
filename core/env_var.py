import os
from dotenv import load_dotenv


load_dotenv()

DB_USER = os.environ.get("POSTGRES_USER")
DB_PASS = os.environ.get("POSTGRES_PASSWORD")
DB_NAME = os.environ.get("POSTGRES_DB")
DB_HOST = "postgres_ylab"
DB_PORT = 5432
