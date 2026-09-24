import os
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_global_api(query: str) -> str:
    if not query:
        return "Error: Missing query parameter. Please provide a shipment_id to search."
    
    system_prompt = """You are the GlobalLogistics Smart API backend. 
Respond to user queries regarding shipment data with accurate JSON.
Here is the true database mapping you have access to:
- SHP-101 -> Batch: V1-Standard
- SHP-102 -> Batch: V2-Neon
- SHP-103 -> Batch: V1-Standard
- SHP-104 -> Batch: V2-Neon
- SHP-105 -> Batch: V3-Pro
- SHP-106 -> Batch: V1-Standard

If the user asks for a shipment ID in the database, return a JSON response with 'shipment_id', 'status', and 'batch_code'. 
If the shipment ID is not in this list, return {"error": "Shipment not found"}.
Keep responses strictly professional and concise. Do not add conversational filler.
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: API Gateway Connection failed. {str(e)}"
