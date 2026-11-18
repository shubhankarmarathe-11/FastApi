from pydantic_settings import BaseSettings,SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):

    email_user:str
    email_pass:str
    internal_token:str
    mysql_user:str
    mysql_pass:str
    mysql_host:str
    mysql_db:str
    redis_host:str
    redis_port:int

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings():
    return Settings()

