from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')
    es_index: str = 'movies, genres, persons'
    es_id_field: str = Field('id')

    redis_host: str = Field('localhost', env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')
    service_url: str = Field('http://127.0.0.1:8000', env='SERVICE_URL')


test_settings = TestSettings()
