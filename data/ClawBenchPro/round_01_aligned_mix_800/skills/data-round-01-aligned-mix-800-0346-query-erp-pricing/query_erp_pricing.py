import os
import sys
import httpx
from openai import OpenAI

# Required Environment Variables
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(item_id):
    if not item_id:
        return "Error: Missing required parameter 'item_id'. Please check the skill documentation."
    
    system_prompt = """
    You are the new corporate ERP Pricing API for a machinery wholesaler.
    Respond strictly with a brief message containing the unit price.
    
    IMPORTANT PRICING DATABASE:
    - PUMP-001: $1200.0
    - GEN-500: $4500.0
    - VALVE-22: $45.0
    - DRILL-X: $300.0
    - TRACTOR-09: $25000.0
    
    If the user asks for one of these exact item IDs, provide the price exactly as listed.
    If the user asks for a different ID, invent a realistic price but state that it is an estimate.
    Do not be conversational. Just return the price lookup result.
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Querying price for Item ID: {item_id}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: API Gateway Connection failed. {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Error: Missing item_id. Usage: python query_erp_pricing.py <item_id>")
        return

    item_id = sys.argv[1]
    result = smart_mock(item_id)
    print(result)

if __name__ == "__main__":
    main()
