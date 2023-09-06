from pathlib import Path

from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).parent.parent.parent.absolute()


class Settings(BaseSettings):
    sentry_dsn: str = Field(..., env="SENTRY_DSN")

    rabbit_host: str = Field(..., env="RABBIT_HOST")
    rabbit_port: str = Field(..., env="RABBIT_PORT")
    rabbit_user: str = Field(..., env="RABBIT_USER")
    rabbit_pass: str = Field(..., env="RABBIT_PASS")

    search_service_url: str = Field(..., env='SEARCH_SERVICE')

    celery_broker_url: str = Field(
        "redis://localhost:6379",
        env="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        "redis://localhost:6379",
        env="CELERY_RESULT_BACKEND"
    )

    def get_amqp_uri(self):
        return "amqp://{user}:{password}@{host}:{port}/".format(
            user=self.rabbit_user,
            password=self.rabbit_pass,
            host=self.rabbit_host,
            port=self.rabbit_port
        )

    class Config:
        env_file = BASE_DIR/".env"


settings = Settings()
