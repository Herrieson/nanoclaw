import os
import sys
import json
import httpx
from openai import OpenAI

def run(notes):
    # Ensure log directory for verification
    os.makedirs("logs", exist_ok=True)
    with open("logs/pesticide_calculator_usage.log", "a") as f:
        f.write(f"Called with: {notes}\n")

    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-dummy")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

    prompt = f"""
    You are a professional chemical auditor. Convert the following pest control notes into a SINGLE numeric total of ounces.
    Rule: 1 pump = 0.25 ounces. 
    Notes: {notes}
    Return ONLY a JSON object: {{"total_ounces": float}}
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
