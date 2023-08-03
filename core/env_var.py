import os

from dotenv import load_dotenv

load_dotenv()

DB_USER = os.environ.get('POSTGRES_USER', 'postgres')
DB_PASS = os.environ.get('POSTGRES_PASSWORD', '1234')
DB_NAME = os.environ.get('POSTGRES_DB', 'postgres_db')
DB_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
DB_PORT = os.environ.get('POSTGRES_PORT', '5432')
