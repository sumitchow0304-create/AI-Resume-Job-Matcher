from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "dev-only-change-me"
    DATABASE_URL: str = "sqlite:///./resume_analyzer.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    UPLOAD_DIR: str = "uploads"
    FRONTEND_DIR: str = ""  # optional override; defaults to ../../frontend

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
