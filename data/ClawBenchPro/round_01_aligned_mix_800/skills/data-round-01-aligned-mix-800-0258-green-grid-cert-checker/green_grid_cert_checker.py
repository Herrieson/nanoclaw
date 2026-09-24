import os
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

http_client = httpx.Client(verify=False)

def check_category(item_id: str) -> str:
    """
    Looks up the official energy category for a given equipment ID.
    Returns a JSON string.
    """
    if not item_id or not isinstance(item_id, str):
        return json.dumps({"error": "Invalid item_id parameter. Must be a string."})
    
    item_id = item_id.strip().upper()
    
    # Ground truth mapping to maintain deterministic objective verification
    hardcoded_db = {
        "A01": "Solar",
        "A02": "Wind",
        "A03": "Fossil",
        "A04": "Hydroponic",
        "A05": "Solar",
        "B01": "Solar",
        "B02": "Hydroponic",
        "B03": "Wind",
        "B04": "Fossil",
        "B05": "Hydroponic"
    }

    if item_id in hardcoded_db:
        return json.dumps({
            "item_id": item_id,
            "category": hardcoded_db[item_id],
            "certified": hardcoded_db[item_id] != "Fossil"
        })

    # LLM fallback for unexpected or creatively generated IDs during Agent interaction
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "You are the Green Grid Certification API. The user will provide an unknown item ID. You must invent a plausible response formatted exactly as JSON with keys: 'item_id' (echo the input), 'category' (pick one of: Solar, Wind, Hydroponic, Fossil), and 'certified' (boolean, true unless Fossil). Output ONLY valid JSON."
                },
                {"role": "user", "content": f"Query item ID: {item_id}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return json.dumps({"error": f"API Connection failed. {str(e)}"})
