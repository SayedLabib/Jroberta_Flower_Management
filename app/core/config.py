from pydantic import BaseSettings, Field
from typing import Optional, List, Dict

class Settings(BaseSettings):
    open_ai_api_key: str = Field(..., env="OPEN_AI_API_KEY")
    app_name: str = Field("Flower_management")
    debug: bool = Field(False, env="DEBUG")

class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"
    case_sensitive = False

    extra = "ignore"
    allow_mutation = False


settings = Settings()

