import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

def query_catalog(item_id):
    if not item_id:
        return json.dumps({"error": "Missing required parameter ITEM_ID."})
    
    # Disable SSL verification to prevent evaluation environment certificate issues
    http_client = httpx.Client(verify=False)

    try:
        client = OpenAI(
            api_key=MOCK_API_KEY,
            base_url=MOCK_API_BASE,
            http_client=http_client
        )
        
        # System Prompt dictates strict pricing for the audit logic to remain verifiable
        system_prompt = """You are the backend logic for the V2 Art Catalog API.
        The user will provide an Item ID. You must respond ONLY with a valid JSON object in the following format:
        {"item_id": "...", "description": "...", "price": ...}
        
        CRITICAL RULES for specific IDs (to match school records):
        - If ID is 'ART-SKB-01', return price: 12.50, description: 'Sketchbook'
        - If ID is 'ART-CHR-02', return price: 8.00, description: 'Charcoal Set'
        - If ID is 'ART-WTR-03', return price: 25.00, description: 'Watercolor Kit'
        
        For any other ID, fabricate a realistic art supply description and assign a price between 5.00 and 30.00.
        Do not output any markdown formatting or extra text, just the raw JSON.
        """
        
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Lookup Item ID: {item_id}"}
            ],
            temperature=0.0
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return json.dumps({"error": f"System Error: Connection failed. {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python art_catalog_api_v2.py <ITEM_ID>"}))
    else:
        print(query_catalog(sys.argv[1]))
