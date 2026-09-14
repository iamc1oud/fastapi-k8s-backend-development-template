from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine

from src.backend import settings

DB = PostgresEngine(
    config={
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
        "database": settings.DB_NAME,
        "user": settings.DB_USER,
        "password": settings.DB_PASSWORD,
    }
)

APP_REGISTRY = AppRegistry(apps=["src.apps.tasks.piccolo_app"])
