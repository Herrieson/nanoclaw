import os
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def skill(file_path: str, extraction_mode: str = "full"):
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use LLM to "decrypt" and parse the structured data out of the messy file
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a data extraction tool. Extract the faculty records (Name, Teaching, Research, Admin) from the provided university log file. Return the result as a raw JSON list."},
                {"role": "user", "content": content}
            ],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Extraction Failed: {str(e)}"

if __name__ == "__main__":
    import sys
    # Simple CLI for the skill
    if len(sys.argv) > 1:
        print(skill(sys.argv[1]))
