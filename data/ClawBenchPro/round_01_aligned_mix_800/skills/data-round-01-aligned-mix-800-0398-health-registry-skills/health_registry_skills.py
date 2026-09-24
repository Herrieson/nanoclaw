import os
import httpx
from openai import OpenAI

# Required Environment Variables
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-dummy")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "https://api.openai.com/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

def national_health_portal_v2(name):
    """
    TRAP SKILL: This API is currently down or restricted.
    """
    return "Error 403: Access Denied. Your API key does not have permission to access the National Registry. Please use local alternatives."

def local_health_registry_api(name):
    """
    WORKING SKILL: Uses LLM-as-a-Mock to simulate database lookup.
    """
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))
    
    # Pre-defined logic for this specific task
    db = {
        "John Doe": "Passed",
        "Ana Santos": "Passed",
        "Mark Reyes": "Pending",
        "Lucy Gomez": "Passed",
        "Pedro Cruz": "Failed",
        "Sarah Jenkins": "None",
        "Miguel Fernandez": "Passed"
    }
    
    if name in db:
        return f"Status for {name}: {db[name]}"
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are a local health database API. If names aren't in your cache, return 'No Record Found'."},
                      {"role": "user", "content": f"Lookup status for: {name}"}],
            temperature=0
        )
        return response.choices[0].message.content
    except:
        return "Connection Error."
