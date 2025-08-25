# API Usage Guide - Flower Bouquet Creator

## Simple & Easy Image Upload

### POST /flower-merge/upload

**Upload 4-6 flower images to create a beautiful bouquet**

### Requirements:
- **Minimum**: 4 images
- **Maximum**: 6 images  
- **File types**: JPG, PNG, GIF, BMP, WEBP
- **Max size**: 10MB per image

### How to Use:

#### In the `/docs` interface:
1. Go to `http://localhost:8066/docs`
2. Find the POST `/flower-merge/upload` endpoint
3. Click "Try it out"
4. Click "Choose Files" and select 4-6 flower images
5. Click "Execute"

**That's it!** No checkboxes, no complicated fields - just upload your images.

#### Examples:

✅ **Valid uploads:**
- 4 images → Creates bouquet
- 5 images → Creates bouquet  
- 6 images → Creates bouquet

❌ **Invalid uploads:**
- 1 image → Error: "Minimum 4 images required"
- 3 images → Error: "Minimum 4 images required" 
- 7 images → Error: "Maximum 6 images allowed"

### Using with Code:

```python
import requests

# Upload 5 flower images
files = [
    ('images', ('flower1.jpg', open('flower1.jpg', 'rb'), 'image/jpeg')),
    ('images', ('flower2.jpg', open('flower2.jpg', 'rb'), 'image/jpeg')),
    ('images', ('flower3.jpg', open('flower3.jpg', 'rb'), 'image/jpeg')),
    ('images', ('flower4.jpg', open('flower4.jpg', 'rb'), 'image/jpeg')),
    ('images', ('flower5.jpg', open('flower5.jpg', 'rb'), 'image/jpeg'))
]

response = requests.post('http://localhost:8066/flower-merge/upload', files=files)
bouquet = response.json()
```

### Response:
The API returns a beautiful bouquet image generated from your flower images using DALL-E 3.

### Health Check:
- GET `/flower-merge/health` - Check service status
- GET `/health` - Check application status
