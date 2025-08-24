import openai
import base64
import io
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from PIL import Image
import requests
from app.core.config import settings
from app.services.Flower_merge.flower_merge_schema import FlowerMergeRequest, FlowerMergeResponse


class FlowerMergeAPIManager:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.open_ai_api_key)

    def _encode_image_to_base64(self, image_bytes: bytes) -> str:
        """Convert image bytes to base64 string for OpenAI API"""
        return base64.b64encode(image_bytes).decode('utf-8')

    def _validate_images(self, images: List[bytes]) -> bool:
        """Validate image inputs - require exactly 4 images"""
        if len(images) != 4:
            raise ValueError(f"Exactly 4 images required. Received: {len(images)}")
        
        for image_bytes in images:
            if len(image_bytes) > settings.max_file_size:
                raise ValueError(f"Image size too large. Maximum allowed: {settings.max_file_size} bytes")
        
        return True

    def merge_flowers(self, request: FlowerMergeRequest) -> FlowerMergeResponse:
        """Main method to merge flower images using GPT-4 vision analysis and DALL-E 3 generation"""
        try:
            # Validate inputs
            self._validate_images(request.images)
            
            if len(request.images) != 4:
                raise ValueError("Exactly 4 images are required")
            
            if settings.debug:
                print(f"Creating flower bouquet from 4 uploaded flower images...")

            # Encode the uploaded images to base64 for analysis
            encoded_images = []
            for i, image_bytes in enumerate(request.images):
                encoded_image = self._encode_image_to_base64(image_bytes)
                encoded_images.append(encoded_image)
                if settings.debug:
                    print(f"Encoded image {i+1} for analysis")

            # First, analyze the uploaded flower images using GPT-4 vision to understand what flowers we have
            analysis_messages = [
                {
                    "role": "system",
                    "content": "You are an expert botanist. Analyze each flower image and identify the exact flower type. Return only the flower names, one per image, in order."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Identify the specific flower type in each of these 4 images. Respond with exactly 4 flower names separated by commas, like: rose, daisy, tulip, carnation. Be precise and use common flower names."
                        }
                    ] + [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        } for encoded_image in encoded_images
                    ]
                }
            ]

            # Get detailed flower analysis from GPT-4 vision for each flower
            detailed_analysis_messages = [
                {
                    "role": "system",
                    "content": "You are an expert botanist and florist. Analyze each flower image in detail and provide comprehensive information about flower characteristics."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "For each of these 4 flower images, analyze and provide detailed information about: 1) Flower name/type, 2) Primary color(s). Format your response as: ' [flower name] - [color] for each image."
                        }
                    ] + [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        } for encoded_image in encoded_images
                    ]
                }
            ]

            # Get basic flower identification from GPT-4 vision
            flower_analysis = self.client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4o which has better vision capabilities
                messages=analysis_messages,
                max_tokens=100,
                temperature=0.3
            )
            
            identified_flowers = flower_analysis.choices[0].message.content.strip()

            # Get detailed flower characteristics using GPT-4 Vision
            detailed_analysis = self.client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4o for detailed vision analysis
                messages=detailed_analysis_messages,
                max_tokens=500,
                temperature=0.3
            )
            
            flower_details = detailed_analysis.choices[0].message.content.strip()
            
            if settings.debug:
                print(f"Identified flowers: {identified_flowers}")
                print(f"Detailed flower analysis: {flower_details}")

            # Create a simple, effective prompt for DALL-E based on the identified flowers
            generation_prompt = f"A realistic photograph of a beautiful flower bouquet arranged together with these 4 flowers: {flower_details}. The flowers are arranged in a proper bouquet formation with stems bundled together, wrapped with ribbon or paper. Professional florist arrangement, natural lighting, photorealistic style with a soft background. No scattered flowers, proper bouquet composition."

            if settings.debug:
                print("Generating flower bouquet with DALL-E...")
                print(f"Using prompt: {generation_prompt}")

            # Use DALL-E for image generation - try DALL-E 2 first for better compatibility
            try:
                image_response = self.client.images.generate(
                    model="dall-e-3",
                    prompt=generation_prompt,
                    size="1024x1024",
                    quality="hd",  # Use HD quality for more realistic results
                    style="natural",  # Use natural style instead of vivid
                    response_format="url",
                    n=1
                )
            except Exception as dalle3_error:
                if settings.debug:
                    print(f"DALL-E 3 failed, trying DALL-E 2: {str(dalle3_error)}")
                # Fallback to DALL-E 2 if DALL-E 3 is not available
                image_response = self.client.images.generate(
                    model="dall-e-2",
                    prompt=generation_prompt,
                    size="1024x1024",
                    response_format="url",
                    n=1
                )
            
            image_url = image_response.data[0].url

            if settings.debug:
                print(f"Generated image URL: {image_url}")






            # Generate a simple title for the bouquet based on identified flowers
            title_messages = [
                {
                    "role": "system",
                    "content": "You create simple, descriptive titles for flower bouquets."
                },
                {
                    "role": "user",
                    "content": f"Create a simple descriptive title (maximum 6 words) for a beautiful flower bouquet made with these flowers: {identified_flowers}"
                }
            ]

            title_response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Use gpt-4o-mini for title generation
                messages=title_messages,
                max_tokens=30,
                temperature=0.5
            )
            
            title = title_response.choices[0].message.content.strip().strip('"').strip("'")

            if settings.debug:
                print(f"Generated title: {title}")
                print(f"Image URL: {image_url}")

            return FlowerMergeResponse(
                title=title,
                imageURL=image_url
            )
            
        except Exception as e:
            if settings.debug:
                print(f"Error in flower merge: {str(e)}")
            raise Exception(f"Failed to merge flowers: {str(e)}")

# Create singleton instance
flower_merge_api_manager = FlowerMergeAPIManager()
