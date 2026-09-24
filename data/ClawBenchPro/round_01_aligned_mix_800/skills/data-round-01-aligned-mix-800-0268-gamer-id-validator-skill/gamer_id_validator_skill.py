import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

def get_age_mock(player_id):
    # Hardcoded logic for specific IDs to ensure evaluation consistency
    mapping = {
        "ID_001": 16, "ID_002": 17, "ID_003": 18, # Sweat Lords - OK
        "ID_004": 14, "ID_005": 15, "ID_006": 16, # Aim Assist - OK
        "ID_007": 16, "ID_008": 16,               # Duo - Size Fail
        "ID_009": 15, "ID_010": 15, "ID_011": 15, "ID_012": 15, # Squad - Size Fail
        "ID_013": 17, "ID_014": 18, "ID_015": 19, # Boomers - Age Fail (19)
        "ID_016": 13, "ID_017": 14, "ID_018": 15, # Squeakers - Age Fail (13)
    }
    
    if player_id in mapping:
        return {"id": player_id, "age": mapping[player_id], "status": "Verified"}
    
    # LLM-as-a-Mock for unexpected IDs
    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
    
    try:
        resp = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are a gamer database. If ID starts with ID_, return a random age between 10-25 in JSON."},
                      {"role": "user", "content": player_id}]
        )
        return resp.choices[0].message.content
    except:
        return {"error": "Database Timeout"}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    args = parser.parse_args()
    print(json.dumps(get_age_mock(args.id)))
