from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Test"
    hostname: str
    username: str
    password: str
    port: int

    # class Config:
        # env_file = ".env"


settings = Settings()
