from groq import Groq
from flask import current_app
import os
import base64
import json

def get_groq_client():
    return Groq(api_key=current_app.config["GROQ_API_KEY"])

def extract_receipt_data(image_path):
    client=get_groq_client()

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
    
    # Strip markdown code blocks if the model wrapped the JSON
    if raw.startswith("```json"):
        raw = raw.replace("```json", "").replace("```", "").strip()
    elif raw.startswith("```"):
        raw = raw.replace("```", "").strip()
        
    return json.loads(raw)