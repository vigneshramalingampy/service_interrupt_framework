from alembic.config import Config

from app.config import settings

config: Config = Config("alembic.ini")
config.set_main_option("sqlalchemy.url", settings.database_url)
config.set_main_option("script_location", "app/migrations")
config.attributes["configure_logger"] = False
