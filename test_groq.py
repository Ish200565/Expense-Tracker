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

raw = response.choices[0].message.content

# --- Helper functions copied in ---
def clean_json_response(raw):
    # Remove markdown code blocks
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    # Find JSON object if mixed with text
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end != 0:
        raw = raw[start:end]

    return raw.strip()

def validate_receipt_data(data):
    if "items" not in data:
        raise ValueError("AI response missing items field")
    if not isinstance(data["items"], list):
        raise ValueError("items must be a list")
    if len(data["items"]) == 0:
        raise ValueError("no items found in receipt")

    for item in data["items"]:
        if "name" not in item:
            item["name"] = "Unknown item"
        if "amount" not in item:
            item["amount"] = 0.00
        if not isinstance(item["amount"], (int, float)):
            try:
                item["amount"] = float(item["amount"])
            except:
                item["amount"] = 0.00

    if "total" not in data:
        data["total"] = sum(item["amount"] for item in data["items"])

    if "currency" not in data:
        data["currency"] = "USD"

    return data
# --- End helpers ---

# Clean and validate the model output
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
