import os
import json
import httpx
from openai import OpenAI

def run(material_name, year="2024"):
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))
    
    prompt = f"Provide a realistic market threshold price for a retail wood audit. Material: {material_name}, Year: {year}. Return only a JSON object like {{'threshold_price': 5500, 'rarity': 'high'}}"

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MOCK_MODEL_NAME", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception:
        # Fallback 逻辑
        thresholds = {"Ebony": 6000, "Oak": 2000, "Mahogany": 5000}
        return json.dumps({"threshold_price": thresholds.get(material_name, 5000), "rarity": "unknown"})

if __name__ == "__main__":
    import sys
    mat = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    print(run(mat))
