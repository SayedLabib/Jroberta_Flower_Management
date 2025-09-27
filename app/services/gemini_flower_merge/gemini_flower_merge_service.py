import logging
import base64
import os
import uuid
import threading
from typing import List
from fastapi import UploadFile
import google.generativeai as genai
from app.core.config import config

logger = logging.getLogger(__name__)


class GeminiFlowerMergeService:
    def __init__(self):
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
        self.temp_dir = "temp_generated_images"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def save_temp_image(self, data_url: str) -> str:
        # Extract base64 data from data URL
        _, base64_data = data_url.split(',', 1)
        filename = f"flower_{uuid.uuid4().hex}.png"
        filepath = os.path.join(self.temp_dir, filename)
        
        # Save image file
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(base64_data))
        
        # Auto-delete after 10 minutes
        threading.Timer(600, lambda: os.remove(filepath) if os.path.exists(filepath) else None).start()
        
        return f"http://localhost:8066/temp-generated-images/{filename}"
    




    async def generate_flower_merge_image(self, image_files: List[UploadFile]) -> List[str]:
        # Prepare content with system prompt
        content = ["Generate a beautiful flower bouquet by merging these images into an artistic arrangement."]
        
        # Add images
        for image_file in image_files:
            image_content = await image_file.read()
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_content))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            content.append(image)
            
        # Generate image
        response = self.model.generate_content(content)
        
        # Extract image data and save as temp file
        images = []
        if hasattr(response, 'candidates'):
            for candidate in response.candidates:
                if hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data.data:
                            # Create data URL and save as temp file
                            base64_data = base64.b64encode(part.inline_data.data).decode('utf-8')
                            data_url = f"data:image/png;base64,{base64_data}"
                            http_url = self.save_temp_image(data_url)
                            images.append(http_url)
        
        return images if images else ["No image generated"]


# Create a singleton instance
gemini_flower_merge_service = GeminiFlowerMergeService()