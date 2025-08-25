from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List, Dict

class Settings(BaseSettings):
    open_ai_api_key: str = Field(..., env="OPEN_AI_API_KEY")
    open_ai_model: str = Field("gpt-4o", env="OPEN_AI_MODEL")
    app_name: str = Field("Flower_management")
    debug: bool = Field(False, env="DEBUG")

    # Essential fields for multi image processing
    min_images_per_request: int = Field(4, env="MIN_IMAGES_PER_REQUEST")
    max_images_per_request: int = Field(6, env="MAX_IMAGES_PER_REQUEST")
    max_file_size: int = Field(10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10 MB

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

settings = Settings()

