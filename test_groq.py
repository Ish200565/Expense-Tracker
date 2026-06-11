from flask import app
from groq import Groq
from dotenv import load_dotenv
import os
import base64
import json
from app.services.groq_services import clean_json_response, validate_receipt_data
from app.services.embedding_service import get_embedding

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

raw = response.choices[0].message.content
parsed = validate_receipt_data(json.loads(clean_json_response(raw)))

# --- Test cases for cleaning ---
raw1 = '```json\n{"items": [{"name": "coffee", "amount": 5.0}], "total": 5.0}\n```'
raw2 = 'Here is the data: {"items": [{"name": "tea", "amount": 3.0}], "total": 3.0}'
raw3 = '{"items": [{"name": "juice"}], "total": 3.0}'

print(json.loads(clean_json_response(raw1)))
print(json.loads(clean_json_response(raw2)))
print(json.loads(clean_json_response(raw3)))

# --- Print parsed receipt ---
print(f"Total: {parsed['total']} {parsed['currency']}")
for item in parsed['items']:
    print(f"  - {item['name']}: {item['amount']}")


embedding = get_embedding("lunch at restaurant")
print("Embedding length:", len(embedding))
print("First 5 values:", embedding[:5])



from app.services.rag_service import search_expenses
results = search_expenses("food restaurant", user_id=3, n_results=3)
print(results)