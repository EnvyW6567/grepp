import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    POSTGRESQL_USER: str = os.getenv('POSTGRESQL_USER')
    POSTGRESQL_PASSWORD: str = os.getenv('POSTGRESQL_PASSWORD')
    POSTGRESQL_DATABASE: str = os.getenv('POSTGRESQL_DATABASE')
    POSTGRESQL_HOST: str = os.getenv('POSTGRESQL_HOST', "localhost")
    POSTGRESQL_PORT: str = os.getenv('POSTGRESQL_PORT', 5432)

    DATABASE_URL = (f'postgresql://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/'
                    f'{POSTGRESQL_DATABASE}')


settings = Settings()
