import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def smart_construction_log_parser_skill(file_path: str, material_type: str):
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    with open(file_path, 'r') as f:
        content = f.read()

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": f"You are a parser. Extract all numerical weights for '{material_type}' from the following log. Return ONLY a JSON object with 'total_weight' and 'unit'."},
                {"role": "user", "content": content}
            ],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Tool Error: {str(e)}"

if __name__ == "__main__":
    # Test logic or direct call
    pass
