from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    threshold: float = 0.5
    # NOTE: this default is only a local-dev fallback. The real value should
    # always come from .env (see DATABASE_URL there) and .env must be
    # git-ignored. Rotate the password below if this repo has ever been
    # pushed anywhere public.
    database_url: str = "mysql+pymysql://root:visionpass123@localhost/visionpass"
    chroma_path: str = "chroma_db"

    class Config:
        env_file = ".env"


settings = Settings()
