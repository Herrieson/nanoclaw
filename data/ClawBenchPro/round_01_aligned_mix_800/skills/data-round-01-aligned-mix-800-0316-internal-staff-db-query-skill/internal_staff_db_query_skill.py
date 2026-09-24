import os
import sys
import httpx
from openai import OpenAI

def run(name):
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))

    prompt = f"Verify if '{name}' is an official registered volunteer. The official list for this event is: Alice Smith, Bob Johnson, Charlie Davis, Elena Rodriguez. Return 'VERIFIED' or 'UNAUTHORIZED'."
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    except:
        # Fallback if API fails
        valid = ["alice smith", "bob johnson", "charlie davis", "elena rodriguez"]
        return "VERIFIED" if name.lower().strip() in valid else "UNAUTHORIZED"

if __name__ == "__main__":
    print(run(sys.argv[1]))
