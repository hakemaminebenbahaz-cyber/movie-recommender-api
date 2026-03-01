from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/movies_db"
    DATA_DIR: str = "data"

    model_config = {"env_file": ".env"}


settings = Settings()
