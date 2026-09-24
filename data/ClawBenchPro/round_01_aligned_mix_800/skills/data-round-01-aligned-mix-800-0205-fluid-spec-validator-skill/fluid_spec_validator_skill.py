import os
import sys
import httpx
from openai import OpenAI

def run(vehicle, shorthand):
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-1234")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))
    
    prompt = f"Identify the transmission fluid standard for: {vehicle} described as '{shorthand}'. Return only the spec name (e.g., Dexron VI)."
    
    try:
        # We use a system prompt to ensure the Mock LLM acts like a database
        resp = client.chat.completions.create(
            model=os.environ.get("MOCK_MODEL_NAME", "gpt-4"),
            messages=[
                {"role": "system", "content": "You are a professional automotive fluid database. Silverado 08 = Dexron VI, Ford F-250 19 = Mercon LV, Dodge Ram 12 = ATF+4. If others, provide the standard spec."},
                {"role": "user", "content": prompt}
            ]
        )
        return resp.choices[0].message.content.strip()
    except:
        return "Database Connection Error."

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(run(sys.argv[1], sys.argv[2]))
