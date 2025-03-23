import os


class Settings:
    POSTGERSQL_USER: str = os.getenv('POSTGRESQL_USER')
    POSTGERSQL_PASSWORD: str = os.getenv('POSTGRESQL_PASSWORD')
    POSTGERSQL_DB: str = os.getenv('POSTGRESQL_DB')
    POSTGERSQL_HOST: str = os.getenv('POSTGRESQL_HOST', "localhost")
    POSTGERSQL_PORT: str = os.getenv('POSTGRESQL_PORT', 5432)

    DATABASE_URL = f'postgresql://{POSTGERSQL_USER}:{POSTGERSQL_PASSWORD}@{POSTGERSQL_HOST}:{POSTGERSQL_PORT}/{POSTGERSQL_DB}'


settings = Settings()
