import os
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-fake-key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def classify_text(text):
    if not text or len(text) < 5:
        return "Error: Input text too short for classification."

    # Use LLM-as-a-Mock for professional classification
    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a Real Estate Emergency Classifier. Categorize the input as 'EMERGENCY' or 'ROUTINE'. Output ONLY valid JSON: {\"classification\": \"...\", \"severity\": 1-10}"},
                {"role": "user", "content": text}
            ],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback logic if API fails
        text_lower = text.lower()
        if "leak" in text_lower or "urgent" in text_lower or "broken" in text_lower or "water" in text_lower:
            return json.dumps({"classification": "EMERGENCY", "severity": 9})
        return json.dumps({"classification": "ROUTINE", "severity": 2})

if __name__ == "__main__":
    import sys
    input_text = " ".join(sys.argv[1:])
    print(classify_text(input_text))
