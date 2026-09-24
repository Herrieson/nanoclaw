import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(part_name):
    if not part_name:
        return json.dumps({"error": "Missing required parameter: part_name"})
    
    system_prompt = (
        "You are the new Cloud ERP API system for a CNC manufacturing company. "
        "The user will provide a machine part name, and you must return its replacement cost in JSON format. "
        "CRITICAL RULES: "
        "1. If the part is exactly 'Spindle_Assembly', you MUST return exactly 850.00. "
        "2. If the part is exactly 'Servo_Motor', you MUST return exactly 1200.00. "
        "3. If the part is exactly 'Coolant_Pump', you MUST return exactly 300.00. "
        "4. For any other part, invent a realistic industrial price. "
        "5. Output ONLY raw JSON, e.g. {\"part\": \"Spindle_Assembly\", \"price\": 850.00}. No markdown, no explanations."
    )
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": part_name}
            ],
            temperature=0.0 # Keep temperature at 0 for strict evaluation compliance
        )
        # Assuming the LLM returns standard JSON
        result = response.choices[0].message.content.strip()
        
        # Clean up potential markdown formatting if the LLM disobeys
        if result.startswith("
