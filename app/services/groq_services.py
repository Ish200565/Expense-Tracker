from groq import Groq
from flask import current_app
import base64
import json

def get_groq_client():
    return Groq(api_key=current_app.config["GROQ_API_KEY"])

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

def extract_receipt_data(image_path):
    client = get_groq_client()

    with open(image_path, "rb") as f:
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
    raw = clean_json_response(raw)
    parsed = json.loads(raw)
    return validate_receipt_data(parsed)
