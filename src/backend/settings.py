import os

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NAME = os.environ.get("DB_NAME", "backend")
DB_USER = os.environ.get("DB_USER", "backend")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "backend")
