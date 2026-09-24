import os
import sys
import httpx
from openai import OpenAI

# Required Environment Variables for Evaluation Infrastructure
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent evaluation sandbox issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def check_ingredient(ingredient):
    if not ingredient:
        return '{"error": "Missing ingredient name. Usage: python botanical_ingredient_checker.py \\"<ingredient>\\""}'
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional cosmetic chemistry ingredient database. The user will provide an ingredient name. Determine if it is strictly 'natural' or 'synthetic' in the context of clean beauty. For example, Dimethicone, Parabens, PEGs, and synthetic preservatives are 'synthetic'. Essential oils, Extracts, Aloe Vera, Beeswax, Shea Butter, and Carrier Oils are 'natural'. Reply STRICTLY in valid JSON format: {\"ingredient\": \"<name>\", \"type\": \"natural|synthetic\"}. Do not output any other text."
                },
                {"role": "user", "content": f"Ingredient: {ingredient}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f'{{"error": "System Error: Botanical DB Connection failed. {str(e)}"}}'

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('{"error": "Missing ingredient name. Usage: python botanical_ingredient_checker.py \\"<ingredient>\\""}')
    else:
        ingredient_name = sys.argv[1]
        print(check_ingredient(ingredient_name))
