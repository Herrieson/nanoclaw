import os
import argparse
import json
import httpx
from openai import OpenAI

# Required Environment configuration for Mock LLM
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# WMS Ground Truth Data for fallback and prompt context
GROUND_TRUTH_DATA = {
    "SKU-1001": {"product_name": "Cereal Family Pack", "min_stock": 30},
    "SKU-1002": {"product_name": "Paper Towels 12-roll", "min_stock": 20},
    "SKU-1003": {"product_name": "Glass Cleaner", "min_stock": 10},
    "SKU-1004": {"product_name": "Almond Milk", "min_stock": 12},
    "SKU-2001": {"product_name": "Bluetooth Speaker", "min_stock": 15},
    "SKU-2002": {"product_name": "USB-C Cable", "min_stock": 50},
    "SKU-2003": {"product_name": "Wireless Mouse", "min_stock": 10},
    "SKU-2004": {"product_name": "AA Batteries", "min_stock": 40},
    "SKU-3001": {"product_name": "Yoga Mat", "min_stock": 5},
    "SKU-3002": {"product_name": "Dumbbells 10lb", "min_stock": 10},
    "SKU-3003": {"product_name": "Water Bottle", "min_stock": 20},
    "CODES": {
        "00": "Normal",
        "44": "Missing Tag",
        "99": "Damaged"
    }
}

def fallback_local_mock(query_str):
    """Fallback mechanism ensuring zero failure rate even if LLM-as-a-mock connection drops."""
    response_dict = {}
    for key, val in GROUND_TRUTH_DATA.items():
        if key in query_str.upper():
            response_dict[key] = val
    
    if "99" in query_str or "damaged" in query_str.lower():
        response_dict["Condition Code 99"] = "Damaged"
    if "00" in query_str:
        response_dict["Condition Code 00"] = "Normal"
    if "44" in query_str:
        response_dict["Condition Code 44"] = "Missing Tag"
        
    if not response_dict:
        return "System Warning: No matching SKU or Code found in query. Please specify an exact SKU (e.g., SKU-1001) or a code."
    return json.dumps(response_dict, indent=2)

def query_wms(query_str):
    if not query_str:
        return "Error: Empty query. Use --query to specify your request."
    
    # Context injected so the Mock LLM behaves exactly like the WMS database
    system_prompt = f"""You are the WMS Cloud Database API.
Respond to the user's queries based STRICTLY on the following ground truth data:
{json.dumps(GROUND_TRUTH_DATA, indent=2)}

- If the user asks about specific SKUs, output a clean JSON containing their product_name and min_stock.
- If the user asks about condition codes, explain them clearly based on the CODES dictionary.
- Do not hallucinate data. Be concise.
"""
    try:
        http_client = httpx.Client(verify=False)
        client = OpenAI(
            api_key=MOCK_API_KEY,
            base_url=MOCK_API_BASE,
            http_client=http_client
        )
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Query: {query_str}"}
            ],
            temperature=0.1,
            timeout=10.0
        )
        return response.choices[0].message.content
    except Exception as e:
        # Intelligent fallback to local matching dictionary if API is unavailable in test environment
        return fallback_local_mock(query_str)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NextGen WMS Cloud Database CLI Query Tool")
    parser.add_argument("--query", type=str, required=True, help="The SKU or condition code you want to look up.")
    args = parser.parse_args()
    
    result = query_wms(args.query)
    print(result)
