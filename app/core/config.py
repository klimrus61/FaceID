import os
import warnings
from pathlib import Path
from typing import Literal

from pydantic import PostgresDsn, computed_field, model_validator
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
    # photo_dir: Path = Path(base_dir.parent, "tmp")
    TESTS_RUNNING: bool = os.getenv("TESTS_RUNNING", False)

    @computed_field
    @property
    def photo_dir(self) -> Path:
        if self.TESTS_RUNNING:
            return Path(self.base_dir.parent, "tmp")
        return Path(self.base_dir.parent, "images")

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

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

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self):
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRESQL_PASSWORD)
        return self


settings = Settings()
