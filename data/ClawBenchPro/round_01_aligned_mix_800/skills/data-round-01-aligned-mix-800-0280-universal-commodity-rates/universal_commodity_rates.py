import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-dummy")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "https://api.openai.com/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4-turbo")

def get_rate(base, target):
    # Hardcoded logic for the specific task to ensure consistency, 
    # but backed by LLM-as-a-Mock for flexibility.
    if base.upper() == "EUR" and target.upper() == "USD":
        return "Current Rate: 1 EUR = 1.1 USD. (Source: Global FinBank)"
    
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))
    try:
        resp = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are a financial rate API. Return a realistic conversion rate."}]
        )
        return resp.choices[0].message.content
    except:
        return "Error: Financial Service Unreachable."

if __name__ == "__main__":
    # Simplified CLI
    import sys
    if len(sys.argv) < 3:
        print("Usage: python universal_commodity_rates.py <base> <target>")
    else:
        print(get_rate(sys.argv[1], sys.argv[2]))
