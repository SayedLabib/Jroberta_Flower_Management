# API Usage Guide - Flower Management System

## Upload Endpoint: POST /flower-merge/upload

### How to Use with 6 Separate Upload Fields

The API supports 1-6 flower images with 6 separate upload fields:

- `flower1` (required) - First flower image
- `flower2` (optional) - Second flower image  
- `flower3` (optional) - Third flower image
- `flower4` (optional) - Fourth flower image
- `flower5` (optional) - Fifth flower image
- `flower6` (optional) - Sixth flower image

### Simplified Usage - No Manual Checkbox Management Required!

✅ **Good News**: You can now use the API without worrying about the "Send empty value" checkboxes!

The API has been improved to automatically handle empty fields. You can:
- Leave optional fields completely empty
- Check or uncheck the "Send empty value" boxes - it doesn't matter
- Only `flower1` (the first field) requires a valid image file

#### Steps to Use:
1. Upload your flower image to `flower1` (required)
2. Upload additional images to any of `flower2-flower6` (optional)
3. Leave unused fields empty (with or without checking the boxes)
4. Click "Execute"

### Examples:

#### Upload 1 Image:
- `flower1`: Select your image file
- `flower2-flower6`: Leave empty (boxes can be checked or unchecked)

#### Upload 3 Images:
- `flower1`: Select first image
- `flower2`: Select second image  
- `flower3`: Select third image
- `flower4-flower6`: Leave empty (boxes can be checked or unchecked)

#### Upload 6 Images:
- `flower1-flower6`: Select all image files

### Alternative Usage (via Code/Postman):

If using the API programmatically, only include the fields you want to use:

```python
import requests

# Example: Upload 2 images
files = {
    'flower1': ('image1.jpg', open('image1.jpg', 'rb'), 'image/jpeg'),
    'flower2': ('image2.jpg', open('image2.jpg', 'rb'), 'image/jpeg')
}

response = requests.post('http://localhost:8066/flower-merge/upload', files=files)
```

### Supported Formats:
- Image types: JPG, PNG, GIF, BMP, WEBP
- Max file size: 10MB per image
- Max images: 6 per request

### Response:
The API will return a beautiful bouquet image generated from your flower images using DALL-E 3.
