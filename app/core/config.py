from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "You Want Ticket"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "YOUR_SECRET_KEY_HERE"  # Change this in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SQLALCHEMY_DATABASE_URI: str = (
        "postgresql://user:password@localhost:5434/you_want_ticket"
    )

    class Config:
        case_sensitive = True


settings = Settings()
