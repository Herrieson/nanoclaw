#!/usr/bin/env python3
import os
import sys
import json

try:
    import httpx
    from openai import OpenAI
except ImportError:
    pass # In actual run, we rely on the env having these, but script guards against immediate crash

# Standard MOCK configurations
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Hardcoded ground truth for exact objective evaluation (prevents LLM hallucination on critical math paths)
STORE_PRICES = {
    "atlanta international market": {
        "tomatoes": 1.20, "onions": 0.80, "rice": 1.00, "peanut_oil": 3.00, "canola_oil": 2.50, "chicken": 3.00, "plantains": 0.90, "spices": 5.00
    },
    "dekalb farmers market": {
        "tomatoes": 1.50, "onions": 0.70, "rice": 0.90, "peanut_oil": 2.80, "canola_oil": 2.80, "chicken": 3.50, "plantains": 0.80, "spices": 4.00
    }
}

def get_price(store_name, ingredient):
    store_key = store_name.lower().strip()
    ing_key = ingredient.lower().strip()
    
    # Return strict values for the evaluation truth
    if store_key in STORE_PRICES and ing_key in STORE_PRICES[store_key]:
        return json.dumps({
            "store": store_name, 
            "ingredient": ingredient, 
            "price": STORE_PRICES[store_key][ing_key]
        })
    
    # 2. Intelligent LLM Mock for unseen queries
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
                {"role": "system", "content": "You are a live grocery store inventory API. Return a realistic price for the requested item in JSON format: {'store': '<store>', 'ingredient': '<item>', 'price': <float>}. If the item or store makes absolutely no sense, return {'error': 'Not found'}."},
                {"role": "user", "content": f"Store: {store_name}, Item: {ingredient}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": f"System Error: API Gateway unavailable. {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing parameters. Usage: script.py <store_name> <ingredient>"}))
        sys.exit(1)
        
    store_arg = sys.argv[1]
    ingredient_arg = sys.argv[2]
    print(get_price(store_arg, ingredient_arg))
