from pydantic_settings import BaseSettings,SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Declare the variables and their expected types
    secret_key: str
    authurl: str
    shorturl:str
    environment:str
    internal_token:str
    google_client_id:str
    mysql_user:str
    mysql_pass:str
    mysql_host:str
    mysql_db:str
    redis_host:str
    redis_port:int

    # Instruct Pydantic to read from the .env file
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings():
    return Settings()


