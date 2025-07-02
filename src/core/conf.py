from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=f"{BASE_DIR}/.env",
        env_file_encoding="utf-8",
    )

    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_DOMAIN: str
    MINIO_CONSOLE_PORT: int
    MINIO_API_PORT: int

    secret_key: str = "super-secret-key"
    algorithm: str = "HS256"

    @property
    def s3_endpoint(self):
        return f"http://{self.MINIO_DOMAIN}:{self.MINIO_API_PORT}/"

    @property
    def sqlite_url(self):
        return f"sqlite+aiosqlite:///{BASE_DIR}/database.db"

    @property
    def psql_url(self):
        return ""


settings = Settings()
