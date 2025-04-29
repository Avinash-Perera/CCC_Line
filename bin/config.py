from pydantic_settings import BaseSettings
from typing import Annotated
import os
from dotenv import load_dotenv

load_dotenv()

pg_username = os.getenv('DB_USERNAME')
pg_password = os.getenv('DB_PASSWORD')
pg_database = os.getenv('DB_MANAGER')
pg_port = os.getenv('DB_PORT')
pg_connection = os.getenv('DB_CONNECTION')
pg_host = os.getenv('DB_HOST')


class Settings(BaseSettings):
    print('hi')
    PG_URL: Annotated[str, ...] = f"{pg_connection}://{pg_username}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
    print('pg_url-->',PG_URL)

# global instance
settings = Settings()



