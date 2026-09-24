import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4-turbo")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_ledger(user_params):
    if not user_params:
        return "Error: Missing query parameters."
    
    system_prompt = """You are the 'Cloud Agri Ledger API' serving a modern farm.
    You MUST base ALL your answers on the following STRICT internal database records for October 2023:
    [Date: 2023-10-01, Item: Alfalfa, Weight: 1500 lbs, Cost: $300]
    [Date: 2023-10-05, Item: Corn, Weight: 800 lbs, Cost: $120]
    [Date: 2023-10-12, Item: Alfalfa, Weight: 2200 lbs, Cost: $440]
    [Date: 2023-10-15, Item: Oats, Weight: 500 lbs, Cost: $100]
    [Date: 2023-10-20, Item: Alfalfa, Weight: 1000 lbs, Cost: $200]
    
    If the user asks about feed purchases or invoices for October 2023, return the relevant records formatted clearly (e.g., in JSON or Markdown tables).
    If they ask about other months, state that records are archived and currently unavailable.
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Query: {user_params}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: API Gateway Connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cloud_agri_ledger_api.py <query>")
    else:
        query_text = " ".join(sys.argv[1:])
        print(query_ledger(query_text))
