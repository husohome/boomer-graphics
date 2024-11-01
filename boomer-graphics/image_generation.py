from openai import OpenAI
from dotenv import load_dotenv

# Set your OpenAI API key
load_dotenv()

def generate_image(prompt) -> str:
    client = OpenAI()

    try:
        response = client.images.generate(
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

if __name__ == "__main__":
    # Example usage
    prompt = "a colorful lotus flower with sunshine and a transparent Buddha in the background."
    image_url = generate_image(prompt)

    if image_url:
        print(f"Generated image URL: {image_url}")
    else:
        print("Failed to generate image.")