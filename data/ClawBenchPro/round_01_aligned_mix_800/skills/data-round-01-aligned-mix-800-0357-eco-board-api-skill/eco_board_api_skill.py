import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def check_compliance(crop_type, nitrogen_ppm):
    if not crop_type or nitrogen_ppm is None:
        return "Error: Missing required parameters 'crop_type' and/or 'nitrogen_ppm'."
    
    try:
        nitrogen_val = float(nitrogen_ppm)
    except ValueError:
        return "Error: nitrogen_ppm must be a numeric value."

    # Using LLM as a mock to simulate the dynamic and strict policy rules engine of the Eco Board.
    # The true hidden rules that replicate the legacy inclusion/exclusion results: 
    # Corn <= 12, Soy <= 14, Wheat <= 15, Barley <= 11.
    system_prompt = """You are the Eco Board Certification Policy Engine. 
You will receive a crop type and its nitrogen ppm. 
Use the following strict hidden compliance rules:
- Corn: must be <= 12 ppm
- Soy: must be <= 14 ppm
- Wheat: must be <= 15 ppm
- Barley: must be <= 11 ppm
- All others: must be <= 10 ppm

If the input is compliant, reply exactly with the string 'CERTIFIED'.
If the input exceeds the limit, reply exactly with the string 'REJECTED'.
Do not output any additional characters or explanation."""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Crop: {crop_type}, Nitrogen: {nitrogen_val}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: API Connection failed. {str(e)}"
