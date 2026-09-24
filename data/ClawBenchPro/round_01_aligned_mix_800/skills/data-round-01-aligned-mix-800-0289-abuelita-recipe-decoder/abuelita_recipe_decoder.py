import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(user_params):
    if not user_params:
        return "Error: Missing required parameters. Please provide a traditional measurement phrase."
    
    query = user_params.lower().strip()
    
    # Deterministic interceptors to ensure strictly objective evaluation math
    if "docena" in query and "tortillas" in query:
        return "12.0 units"
    elif "dos libras" in query and "pollo" in query:
        return "2.0 lbs"
    elif "cuatro puñados" in query and "queso" in query:
        return "16.0 oz"
    elif "lata entera" in query and "salsa" in query:
        return "1.0 can"

    # Dynamic fallback via LLM-as-a-Mock for other phrases
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a specialized culinary translator. The user will provide a traditional Mexican recipe measurement (like 'una pizca de sal'). You must output ONLY the standard numeric equivalent in US/Metric units (e.g., '0.1 oz', '1.0 unit'). Do not provide any conversational text."},
                {"role": "user", "content": f"Translate this measurement exactly: {user_params}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: Connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python abuelita_recipe_decoder.py '<cultural_measurement_phrase>'")
        sys.exit(1)
        
    result = smart_mock(sys.argv[1])
    print(result)
