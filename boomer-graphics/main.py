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


def split_text(text, max_length=6):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        # Check if adding the word would exceed the max_length
        if len(current_line) + len(word) + 1 > max_length:
            lines.append(current_line.strip())
            current_line = word
        else:
            current_line += " " + word

    # Append the last line if it has content
    if current_line:
        lines.append(current_line.strip())

    # Force split lines that exceed max_length
    final_lines = []
    for line in lines:
        while len(line) > max_length:
            final_lines.append(line[:max_length])
            line = line[max_length:]
        final_lines.append(line)

    return "\n".join(final_lines)
# add text
def add_text_overlay(
        image_url,
        text,
        x=40,
        y=40,
        placement='south_west',
        color='#FF0000',
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
        split_text_length: int = 6,
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
    if not (exact_text[:5] + image_prompt[:5] in boomer_graphics) and not (text_prompt[:5] + image_prompt[:5] in boomer_graphics):
        text = ""
        if text_prompt and not exact_text:
            text = chatgpt_completion(text_prompt)
        else:
            text = exact_text
        transformed_url = add_text_overlay(image_url, split_text(text, split_text_length), x, y, placement, color)
        
        
        upload_result = cloudinary.uploader.upload(
            transformed_url, public_id=text[:5] + image_prompt[:5])
        boomer_graphics[text[:5] + image_prompt[:5]] = upload_result["secure_url"]
    
    
    optimize_url, _ = cloudinary_url(boomer_graphics[text[:5] + image_prompt[:5]], fetch_format=fetch_format, quality=quality,  width=width, height=height, crop=crop, gravity=gravity)
    return optimize_url

if __name__ == "__main__":
    # Example usage
    import random
    health_advice = """
    健康資訊: 這位55歲女性客戶的健康狀況令人擔憂，有多項指標顯示健康風險偏高，需要積極介入改善。她BMI超標、有不良生活習慣（熬夜、吸菸/飲酒/嚼檳榔）、家族病史（癌症及其他重症），且自身也處於亞健康狀態。雖然每日步數達標，但高死亡率、住院率、手術率及癌症風險預測都偏高，顯示運動量雖足，但健康狀況仍需全面改善。財務狀況方面，個人經濟能力較低，但家庭經濟狀況良好，這表示有資源可以投入健康管理。

    飲食建議 (基於提供的乳癌飲食指南，並考量整體健康狀況):

    **可食：**瘦肉（例如雞胸肉、里肌肉）、鯖魚、秋刀魚、鮭魚（富含Omega-3脂肪酸）、糙米、薏仁、燕麥（富含膳食纖維）、地瓜葉、黑木耳、菇類（提供維生素和礦物質）、豆腐、豆漿、豆干（優質植物性蛋白質）、橄欖油（健康油脂）。
    **禁食：**油炸食物、酒精、豬油、牛油、三層肉（高飽和脂肪，不利健康）。
    **需控制：**紅肉、加工肉品、高糖食物、精緻澱粉（白米飯、白麵包等）。
    三個月健康改善計畫：

    第一個月：調整生活習慣，建立健康基礎

    戒除不良習慣： 逐步減少並戒除吸菸/飲酒/嚼檳榔。尋求專業協助或加入戒癮團體。
    規律作息： 避免熬夜，盡量晚上11點前就寢，確保充足睡眠。
    飲食調整： 參考上述飲食建議，開始逐步調整飲食，減少不健康食物攝取，增加蔬果、全穀類、優質蛋白質的比例。
    壓力管理： 由於家中有人罹癌，壓力可能較大，建議學習壓力管理技巧，例如冥想、瑜珈、深呼吸等。
    第二個月：強化營養，提升免疫力

    均衡飲食： 參考每日建議攝取量，制定個人化飲食計畫。
    補充營養素： 可諮詢營養師或醫師，評估是否需要額外補充維生素、礦物質等營養素，以提升免疫力。
    規律運動： 維持每日步數，並加入其他運動，例如游泳、快走、瑜珈等，增強體能。
    第三個月：持續監控，鞏固成果

    定期健康檢查： 密切追蹤健康指標，例如血壓、血糖、血脂等。
    維持健康習慣： 將前兩個月建立的健康習慣融入日常生活，並持續監控及調整。
    尋求專業支持： 持續與營養師、醫師或其他醫療專業人員保持聯繫，獲得持續的指導和支持。
    每日建議攝取量 (需根據個人活動量和代謝率調整):

    由於客戶BMI超標，需要控制總熱量攝取，以達到減重的目標。建議每日攝取量如下（僅供參考，需由專業營養師根據個案情況調整）：

    全穀雜糧類： 1.5-2碗 (以糙米、燕麥、全麥麵包為主)
    豆魚蛋肉類： 3-4份 (以低脂肉類、魚類、豆腐、豆漿為主)
    蔬菜類： 3-4份 (各色蔬菜，盡量多樣化)
    水果類： 2-3份 (選擇低GI水果，例如芭樂、蘋果、奇異果)
    乳品類： 1-2杯 (低脂或脫脂牛奶)
    油脂類： 2-3湯匙 (以橄欖油、堅果等健康油脂為主)
    堅果種子類： 1份
    水分： 2000cc以上
    重要提醒： 以上僅為初步建議，務必尋求專業營養師的協助，根據個人情況制定更精確的飲食和運動計畫。 定期健康檢查和與醫療專業人員保持聯繫至關重要。 家人的支持和鼓勵也是成功的重要因素。
    """
    
    image_prompts = [
        "a serene picture of a flower basket with a dominant orchid in the background. In the foreground there's a translucent city-girl swiping a cell phone and listening to music with her pink headphone with ennui.",
        "a cute, caligraphy based money god in a random serene background that's also caligraphy based, with maybe a floating gold fish",
        "a doraemon-like cartoonish creature in cartoon style and a strong color background that fits the aestheics of boomers.",
        "a random serene realistic scenery spot that fits boomer aesthetics",
        "a serene picture of a cute money god (財神 or 彌勒佛), translucent, but caligraphy style. There's also a tree that is similar to the logo of CathayLife insurance"
        "a dominant lotus flower with sunshine and a transparent Buddha in the background.",
    ]
    boomer_graphics = generate_boomer_graphs(
        image_prompt=random.choice(image_prompts), 
        text_prompt=f"summarize this health advice and condense it into somewhere between 5 to 10 Traditional Chinese characters. <advice>{health_advice}</advice> You MUST ensure it's in traditional Chinese and only contain 5 to 10 words. Then, add '早安，' in front of it.", #祝你今天愉快！\n多吃白肉有益身體健康",
        placement=random.choice(['south_west', 'south_east', 'north_west', 'north_east']),
        color=random.choice(['#FF0000', '#00FF00', '#0000FF', "#FFFFFF", "#000000"]),
    )
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

