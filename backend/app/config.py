from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    threshold: float = 0.5
    database_url: str = "mysql+pymysql://root:visionpass123@localhost/visionpass"
    chroma_path: str = "chroma_db"

    class Config:
        env_file = ".env"


settings = Settings()