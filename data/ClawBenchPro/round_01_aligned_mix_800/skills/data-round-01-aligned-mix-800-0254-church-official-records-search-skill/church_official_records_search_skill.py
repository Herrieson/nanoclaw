import sys
import json
import os
import httpx
from openai import OpenAI

def search_records(name):
    # Mock Database of approved members
    whitelist = ["Hector Ramirez", "Luis Perez", "Father Thomas", "Maria Gonzalez"]
    
    # LLM-as-a-Mock logic for fuzzy matching
    client = OpenAI(
        api_key=os.environ.get("MOCK_API_KEY", "sk-xxx"),
        base_url=os.environ.get("MOCK_API_BASE", "http://localhost/v1"),
        http_client=httpx.Client(verify=False)
    )
    
    prompt = f"Determine if the name '{name}' matches any of these approved members: {whitelist}. Return JSON format: {{'is_approved': bool, 'official_name': str or null}}"
    
    try:
        response = client.chat.completions.create(
            model=os.environ.get("MOCK_MODEL_NAME", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback to simple matching if API fails
        for member in whitelist:
            if name.split()[0].lower() in member.lower():
                return json.dumps({"is_approved": True, "official_name": member})
        return json.dumps({"is_approved": False, "official_name": None})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python church_official_records_search_skill.py <name>")
    else:
        print(search_records(sys.argv[1]))
