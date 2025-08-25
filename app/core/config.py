from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List, Dict

class Settings(BaseSettings):
    open_ai_api_key: str = Field(..., env="OPEN_AI_API_KEY")
    
    # AI Model configurations
    vision_model: str = Field("gpt-4o", env="VISION_MODEL")  # For flower analysis
    chat_model: str = Field("gpt-4o-mini", env="CHAT_MODEL")  # For title generation
    image_model_primary: str = Field("dall-e-3", env="IMAGE_MODEL_PRIMARY")  # Primary image generation
    image_model_fallback: str = Field("dall-e-2", env="IMAGE_MODEL_FALLBACK")  # Fallback image generation
    
    app_name: str = Field("Flower_Management_Simplified")
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

