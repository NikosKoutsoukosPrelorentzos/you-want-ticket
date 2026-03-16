from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "You Want Ticket"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "YOUR_SECRET_KEY_HERE"  # Change this in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GOOGLE_CLIENT_ID: str = ""
    SQLALCHEMY_DATABASE_URI: str = (
        "postgresql://user:password@localhost:5434/you_want_ticket"
    )


settings = Settings()
