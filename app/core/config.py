from pathlib import Path

from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    app_name: str = "Awesome API"
    API_V1_STR: str = "/api/v1"
    admin_email: str = "admin@admin.com"
    items_per_user: int = 50
    base_dir: Path = Path(__file__).parent.parent
    tmp_dir: Path = Path(base_dir.parent, "tmp")
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_HOSTNAME: str
    POSTGRESQL_PORT: int
    POSTGRESQL_DB_NAME: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_HOSTNAME,
            port=self.POSTGRESQL_PORT,
            path=self.POSTGRESQL_DB_NAME,
        )


settings = Settings()
