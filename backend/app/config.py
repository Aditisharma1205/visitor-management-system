from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    threshold: float = 0.5

    class Config:
        env_file = ".env"


settings = Settings()