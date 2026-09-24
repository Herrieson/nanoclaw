import os
import argparse
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

def get_taxonomy_tag(query):
    if not query:
        return "Error: Missing query string."
        
    http_client = httpx.Client(verify=False)
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
    
    system_prompt = """You are a specialized kitchen safety taxonomy mapper API.
The user will provide a colloquial dietary restriction. 
You must return a list of exactly matching proprietary tags from the following list ONLY. Do not write anything else.
Available tags: ["T1-Vegan_Strict", "T2-Dairy_Intolerant", "T4-Peanut_Fatal", "T5-Vegetarian", "T9-Gluten_Sensitive"]

Mapping Rules:
- No animal products / no meat, no eggs, no milk -> ["T1-Vegan_Strict"]
- Peanut allergy / swell up near peanuts -> ["T4-Peanut_Fatal"]
- Milk makes sick / no milk -> ["T2-Dairy_Intolerant"]
- No meat -> ["T5-Vegetarian"]
- Celiac / no gluten -> ["T9-Gluten_Sensitive"]

Output format: Just the python-style list of strings, e.g., ["T1-Vegan_Strict", "T4-Peanut_Fatal"]. If none apply, output []."""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {query}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: API Connection failed. {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map colloquial dietary queries to proprietary tags.")
    parser.add_argument("--query", required=True, help="Colloquial description (e.g., 'milk makes her sick')")
    args = parser.parse_args()
    
    print(get_taxonomy_tag(args.query))
