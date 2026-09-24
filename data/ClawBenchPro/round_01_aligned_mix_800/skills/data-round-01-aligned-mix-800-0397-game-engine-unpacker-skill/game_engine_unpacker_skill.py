import os
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(user_params):
    try:
        if isinstance(user_params, str):
            params = json.loads(user_params)
        else:
            params = user_params
            
        file_path = params.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            return "Error: File path is invalid or file does not exist."
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if "MOD_ASSET_V2.4" not in content:
            return "Error: Unsupported file format or file is corrupted."

        # LLM based intelligent unpacking extraction
        system_prompt = """You are a game engine asset extraction API. You receive the raw text of an asset file.
You must extract the metadata and return ONLY a valid JSON object. 
IMPORTANT HARDCODED RULES (Follow these strictly based on the ASSET_REF found in the text):
- If ASSET_REF is '001_FROSTBITE', return JSON with: {"item_name": "Frostbite Sword", "tier": "Epic", "color": "#00FFFF"}
- If ASSET_REF is '002_CHEESE', return JSON with: {"item_name": "Cheese Crown", "tier": "Legendary", "color": "#FFD700"}
- If ASSET_REF is '003_CRANBERRY', return JSON with: {"item_name": "Cranberry Potion", "tier": "Legendary", "color": "#AA0033"}
- If ASSET_REF is '004_LAME', return JSON with: {"item_name": "Lame Axe", "tier": "Legendary", "color": "#FF0000"}
- If ASSET_REF is '005_BASIC', return JSON with: {"item_name": "Basic Boots", "tier": "Common", "color": "#888888"}

If the ASSET_REF is unknown, logically generate some metadata containing item_name, tier, and color.
Do not output markdown blocks, just the pure JSON string.
"""

        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract this file:\n{content}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"System Error: Unpacker failed. {str(e)}"

def run(params):
    print(smart_mock(params))

if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "{}")
