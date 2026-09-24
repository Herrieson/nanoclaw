import os
import sys
import json
import httpx
from openai import OpenAI

# Required environment variables for LLM-as-a-Mock robustness
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# Disable SSL verification to prevent evaluation environment cert issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(solar, water):
    if not solar or not water:
        return json.dumps({"error": "Missing parameters. Required: solar_kwh and water_gallons"})
    
    prompt = (
        f"The user has saved {solar} kWh of solar energy and {water} gallons of water. "
        "Calculate a realistic 'eco_impact_score' (an integer between 1 and 1000). "
        "Return ONLY a pure JSON object with the key 'eco_impact_score'. Do not return any other text, markdown formatting, or explanation."
    )
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a backend cloud API calculating eco impact scores."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        
        # Cleanup potential markdown ticks from the LLM
        if content.startswith("
