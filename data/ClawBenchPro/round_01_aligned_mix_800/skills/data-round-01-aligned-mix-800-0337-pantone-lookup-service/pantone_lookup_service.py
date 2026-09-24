import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def lookup_pantone(hex_code):
    prompt = f"""
    You are a professional Pantone Color Expert. 
    Convert the following Hex code to its most famous nearest Pantone Name (e.g., 'Pantone 18-2120 Honeysuckle').
    Hex: {hex_code}
    Return ONLY the name.
    """
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Database Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Hex code required.")
    else:
        print(lookup_pantone(sys.argv[1]))
