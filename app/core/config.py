from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Awesome API"
    API_V1_STR: str = "/api/v1"
    admin_email: str = "admin@admin.com"
    items_per_user: int = 50
    base_dir: Path = Path(__file__).parent.parent
    tmp_dir: Path = Path(base_dir.parent, "tmp")
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )


settings = Settings()
