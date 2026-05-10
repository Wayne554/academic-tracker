from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    DATABASE_URL: str = "sqlite:///./academic_tracker.db"
    OPENALEX_BASE_URL: str = "https://api.openalex.org"
    INIT_ADMIN_USERNAME: str = "admin"
    INIT_ADMIN_PASSWORD: str = "admin123"
    INIT_ADMIN_EMAIL: str = "admin@example.com"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
