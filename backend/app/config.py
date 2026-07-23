from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./hausbank.db"
    ANTHROPIC_API_KEY: str = ""         # leave empty → agents run in mock mode
    ENVIRONMENT: str = "development"

    # Agent tuning — adjust these against real incident history
    HEALER_CONFIDENCE_THRESHOLD: float = 0.85
    SIMILARITY_TOP_K: int = 10
    MAX_HOP_COUNT: int = 3
    MAX_RESOLUTION_MINUTES: int = 20

    class Config:
        env_file = ".env"


settings = Settings()
