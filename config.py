from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Default App Name"
    debug_mode: bool = False
    database_url: str
    secret_key: str
    ollama_host: str = "http://localhost:11434"

    # Load parameters directly from the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Cache the settings instance so we don't re-read the .env file on every single API request
@lru_cache
def get_settings():
    return Settings()