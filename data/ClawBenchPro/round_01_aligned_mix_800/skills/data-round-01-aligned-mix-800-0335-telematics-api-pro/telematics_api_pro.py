import os
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mocking
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# Disable SSL verification for reliable testing environment execution
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def telematics_api_pro(payload_string: str) -> str:
    """
    Uses LLM-as-a-Mock to intelligently decode a proprietary truck telematics payload.
    """
    if not payload_string:
        return json.dumps({"status": "error", "message": "Missing payload_string parameter."})
        
    system_prompt = (
        "You are an enterprise-grade Truck Telematics Decoder API. "
        "The user will provide a raw payload string from an OBD2 scanner. "
        "If the payload is EXACTLY 'VSS_ERR_8F3A2B', you MUST return this exact JSON string: "
        "{\"status\": \"success\", \"diagnostic\": \"Vehicle Speed Sensor Signal Drop Detected\", \"recovered_miles\": 255.5}. "
        "For any other payload string, generate a plausible JSON response with a fake 'recovered_miles' float value and a different diagnostic string."
    )
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Payload: {payload_string}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"status": "fatal_error", "message": f"Connection to Telematics Cloud failed: {str(e)}"})
