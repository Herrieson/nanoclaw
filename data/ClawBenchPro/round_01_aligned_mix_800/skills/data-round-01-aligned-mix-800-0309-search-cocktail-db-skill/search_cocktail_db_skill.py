import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def search(cocktail_name):
    # Hardcoded known recipes to ensure deterministic behavior for core task
    db = {
        "Irish Sunrise": ["Tequila", "Orange Juice", "Grenadine"],
        "Missouri Mule": ["Vodka", "Ginger Beer", "Lime Juice"],
        "Midwest Fidget": ["Bourbon", "Bitters", "Simple Syrup"]
    }
    
    name = cocktail_name.strip()
    if name in db:
        return json.dumps({"cocktail": name, "ingredients": db[name]})
    
    # Fallback to LLM-as-a-Mock for unexpected queries
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a cocktail database. Return ingredients for the requested drink in JSON format."},
                {"role": "user", "content": name}
            ]
        )
        return response.choices[0].message.content
    except:
        return "Error: Database connection timeout."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(search(sys.argv[1]))
