from groq import Groq
from dotenv import load_dotenv
import os
import base64
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

with open("sample.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

response = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                },
                {
                    "type": "text",
                    "text": """You are a receipt scanner. Extract all items and amounts from this receipt.
Return ONLY a JSON object in this exact format, nothing else, no extra text:
                                {
                                    "items": [
                                        {"name": "item name", "amount": 0.00}
                            ],
                                    "total": 0.00,
                                    "currency": "currency code"
                                }"""
                }
            ]
        }
    ]
)

# print(response.choices[0].message.content)


raw = response.choices[0].message.content

parsed = json.loads(raw)

print(f"Total: {parsed['total']} {parsed['currency']}")
for item in parsed['items']:
    print(f"  - {item['name']}: {item['amount']}")