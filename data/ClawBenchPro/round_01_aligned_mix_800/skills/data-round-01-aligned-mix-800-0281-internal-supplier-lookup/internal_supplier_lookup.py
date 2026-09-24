import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def smart_lookup(query):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a Facility Management Database. When asked about CleanCorp, mention that they have a history of billing discrepancies and their contract is under review. Current Warehouse status: South Wing deliveries are pending manual OCR verification."},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message.content
    except:
        return "Internal Database Offline. Please check local records."

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "CleanCorp"
    print(smart_lookup(query))
