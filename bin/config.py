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

MPGS_API_VERSION = os.getenv('MPGS_API_VERSION')
MPGS_BASE_URL = os.getenv('MPGS_BASE_URL')
RETURN_URL = os.getenv('RETURN_URL')
APP_URL = os.getenv('APP_URL')

SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_ENCRYPTION = os.getenv('SMTP_ENCRYPTION')
SMTP_SENDER_MAIL = os.getenv('SMTP_SENDER_MAIL')
SMTP_SENDER_PW = os.getenv('SMTP_SENDER_PW')
OTP_INTERVAL = os.getenv('OTP_INTERVAL', '2')

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES')

# Load merchant credentials from .env
MERCHANT_CREDENTIALS = {
    "LKR": {
        "merchant_id": os.getenv("MPGS_LKR_MERCHANT_ID"),
        "api_username": os.getenv("MPGS_LKR_USERNAME"),
        "api_password": os.getenv("MPGS_LKR_PASSWORD")
    },
    "GBP": {
        "merchant_id": os.getenv("MPGS_GBP_MERCHANT_ID"),
        "api_username": os.getenv("MPGS_GBP_USERNAME"),
        "api_password": os.getenv("MPGS_GBP_PASSWORD")
    },
    "USD": {
        "merchant_id": os.getenv("MPGS_USD_MERCHANT_ID"),
        "api_username": os.getenv("MPGS_USD_USERNAME"),
        "api_password": os.getenv("MPGS_USD_PASSWORD")
    },
    "EUR": {
        "merchant_id": os.getenv("MPGS_EUR_MERCHANT_ID"),
        "api_username": os.getenv("MPGS_EUR_USERNAME"),
        "api_password": os.getenv("MPGS_EUR_PASSWORD")
    }
}

class Settings(BaseSettings):
    PG_URL: Annotated[str, ...] = f"{pg_connection}://{pg_username}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
    print('pg_url-->',PG_URL)

    # Email
    SMTP_HOST: str = SMTP_HOST
    SMTP_PORT: int = int(SMTP_PORT) if SMTP_PORT else 465
    SMTP_ENCRYPTION: str = SMTP_ENCRYPTION
    SMTP_SENDER_MAIL: str = SMTP_SENDER_MAIL
    SMTP_SENDER_PW: str = SMTP_SENDER_PW
    OTP_INTERVAL: int = int(OTP_INTERVAL)

    # JWT
    SECRET_KEY: str = SECRET_KEY
    ALGORITHM: str = ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(ACCESS_TOKEN_EXPIRE_MINUTES)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(REFRESH_TOKEN_EXPIRE_MINUTES)


# global instance
settings = Settings()



