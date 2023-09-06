from logging import config as logging_config

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(..., env='PROJECT_NAME')
    REDIS_HOST: str = Field(..., env='REDIS_HOST')
    REDIS_PORT: int = Field(..., env='REDIS_PORT')
    ELASTIC_HOST: str = Field(..., env='ELASTIC_HOST')
    ELASTIC_PORT: int = Field(..., env='ELASTIC_PORT')

    class Config:
        env_file = '.env'


settings = Settings()
