import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv
import os
load_dotenv()

# Configuration       
cloudinary.config( 
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
    api_key = os.getenv("CLOUDINARY_API_KEY"), 
    api_secret = os.getenv("CLOUDINARY_API_SECRET"), # Click 'View API Keys' above to copy your API secret
    secure=True
)

def add_text_overlay(
        image_url,
        text,
        x=40,
        y=40,
        placement='south_west',
        color='#FF0000'
    ):
    result = cloudinary.uploader.upload(image_url, 
        public_id="flower_with_text",
        overwrite=True,
        transformation=[
            {'width': 800, 'crop': 'scale'},
            {'overlay': {'font_family': "Arial", 'font_size': 64, 'text': text},
             'gravity': 
                 placement, 
                 'x': x,
                 'y': y,
                 'color':
                     color
            }
        ])
    return result['secure_url']

flower_url = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-NpR5F7M78Nqcd5kvYThxGTYJ/user-eOsS5q7WZpBaF0GKNJnKjOen/img-G3ooUhHpjhSXixDHfMCrp0yI.png?st=2024-11-01T08%3A30%3A17Z&se=2024-11-01T10%3A30%3A17Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-11-01T01%3A22%3A51Z&ske=2024-11-02T01%3A22%3A51Z&sks=b&skv=2024-08-04&sig=734enW8NJFBrX3t/7QeJvf71V8uG96bOyXxmHWO3lvA%3D"
# Upload an image
upload_result = cloudinary.uploader.upload(
    flower_url,
    public_id="flower")
print(upload_result["secure_url"])

# Usage
text = "早安，祝你今天愉快！\n多吃白肉有益身體健康"
new_image_url = add_text_overlay(flower_url, text, x=20, y=150)
print(new_image_url)

# Optimize delivery by resizing and applying auto-format and auto-quality
optimize_url, _ = cloudinary_url("flower", fetch_format="auto", quality="auto")
print(optimize_url)

# Transform the image: auto-crop to square aspect_ratio
auto_crop_url, _ = cloudinary_url("flower", width=500, height=500, crop="auto", gravity="auto")
print(auto_crop_url)

