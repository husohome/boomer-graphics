import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
# Configuration       
cloudinary.config( 
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
    api_key = os.getenv("CLOUDINARY_API_KEY"), 
    api_secret = os.getenv("CLOUDINARY_API_SECRET"), # Click 'View API Keys' above to copy your API secret
    secure=True
)

original_images = {} # image-id and url pairs
boomer_graphics = {}
chatgpt_client = OpenAI()  # Replace with your actual API key

def chatgpt_completion(input_text):
    response = chatgpt_client.chat.completions.create(
        model="gpt-4o",  # You can use "gpt-4" if you have access
        messages=[
            {"role": "user", "content": input_text}
        ]
    )

    return response.choices[0].message.content

# background
def generate_image(prompt) -> str: # this returns an image url

    try:
        response = chatgpt_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        # The URL of the generated image
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# add text
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

def complete_transform(image_url, transformation):
    result = cloudinary.uploader.upload(image_url, 
        public_id="flower_with_text",
        overwrite=True,
        transformation=transformation)
    return result['secure_url']


def generate_boomer_graphs(
        text_prompt: str = "health advice in fewer than 10 Traditional Chinese characters (Taiwan!) starting with 早安", # prompt to generate text
        image_prompt: str = "a colorful lotus flower with sunshine and a transparent Buddha in the background.", # for image
        x=20,
        y=150,
        placement='south_west',
        color='#FF0000',
        exact_text: str = "", # overwrites text_prompt
        width: int = 500,
        height: int = 500,
        quality: str = "auto",
        fetch_format: str = "auto",
        crop: str = "auto",
        gravity: str = "auto"
    ):

    if not image_prompt in original_images:
        image_url = generate_image(image_prompt)
        original_images[image_prompt] = image_url
    
    image_url = original_images[image_prompt]
    if not (exact_text + image_prompt in boomer_graphics) and not (text_prompt + image_prompt in boomer_graphics):
        text = ""
        if text_prompt and not exact_text:
            text = chatgpt_completion(text_prompt)
        else:
            text = exact_text
        transformed_url = add_text_overlay(image_url, text, x, y, placement, color)
        upload_result = cloudinary.uploader.upload(transformed_url, public_id=text + image_prompt)
        boomer_graphics[text + image_prompt] = upload_result["secure_url"]
    
    
    optimize_url, _ = cloudinary_url(boomer_graphics[text + image_prompt], fetch_format=fetch_format, quality=quality,  width=width, height=height, crop=crop, gravity=gravity)
    return optimize_url

if __name__ == "__main__":
    # Example usage
    boomer_graphics = generate_boomer_graphs()
    with open('boomer_graphics.txt', 'w') as f:
        f.write(str(boomer_graphics))
    print(boomer_graphics)



# flower_url = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-NpR5F7M78Nqcd5kvYThxGTYJ/user-eOsS5q7WZpBaF0GKNJnKjOen/img-G3ooUhHpjhSXixDHfMCrp0yI.png?st=2024-11-01T08%3A30%3A17Z&se=2024-11-01T10%3A30%3A17Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-11-01T01%3A22%3A51Z&ske=2024-11-02T01%3A22%3A51Z&sks=b&skv=2024-08-04&sig=734enW8NJFBrX3t/7QeJvf71V8uG96bOyXxmHWO3lvA%3D"
# # Upload an image
# upload_result = cloudinary.uploader.upload(
#     flower_url,
#     public_id="flower")
# print(upload_result["secure_url"])

# # Usage
# text = "早安，祝你今天愉快！\n多吃白肉有益身體健康"
# new_image_url = add_text_overlay(flower_url, text, x=20, y=150)
# print(new_image_url)

# # Optimize delivery by resizing and applying auto-format and auto-quality
# optimize_url, _ = cloudinary_url("flower", fetch_format="auto", quality="auto")
# print(optimize_url)

# # Transform the image: auto-crop to square aspect_ratio
# auto_crop_url, _ = cloudinary_url("flower", width=500, height=500, crop="auto", gravity="auto")
# print(auto_crop_url)

