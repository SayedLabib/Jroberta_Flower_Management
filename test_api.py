#!/usr/bin/env python3
"""
Test script to verify the API accepts different numbers of images
"""
import requests
import io
from PIL import Image

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color=(255, 0, 0))  # Red image
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def test_api_with_different_image_counts():
    """Test the API with different numbers of images"""
    base_url = "http://localhost:8066"
    
    # Test with 1 image
    print("Testing with 1 image...")
    test_img = create_test_image()
    files = {
        'flower1': ('test1.jpg', test_img, 'image/jpeg')
    }
    response = requests.post(f"{base_url}/flower-merge/upload", files=files)
    print(f"1 image - Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    
    # Test with 2 images
    print("\nTesting with 2 images...")
    test_img1 = create_test_image()
    test_img2 = create_test_image()
    files = {
        'flower1': ('test1.jpg', test_img1, 'image/jpeg'),
        'flower2': ('test2.jpg', test_img2, 'image/jpeg')
    }
    response = requests.post(f"{base_url}/flower-merge/upload", files=files)
    print(f"2 images - Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    
    # Test with 3 images
    print("\nTesting with 3 images...")
    test_img1 = create_test_image()
    test_img2 = create_test_image()
    test_img3 = create_test_image()
    files = {
        'flower1': ('test1.jpg', test_img1, 'image/jpeg'),
        'flower2': ('test2.jpg', test_img2, 'image/jpeg'),
        'flower3': ('test3.jpg', test_img3, 'image/jpeg')
    }
    response = requests.post(f"{base_url}/flower-merge/upload", files=files)
    print(f"3 images - Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_api_with_different_image_counts()
