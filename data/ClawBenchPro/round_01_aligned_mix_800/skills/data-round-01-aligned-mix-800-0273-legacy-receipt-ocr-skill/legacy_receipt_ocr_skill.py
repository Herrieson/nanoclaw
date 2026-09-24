import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def main():
    try:
        args = json.loads(sys.argv[1])
        file_path = args.get("file_path")
        
        with open(file_path, 'r') as f:
            content = f.read()

        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an OCR expert. Extract items, categories, and prices from this messy scan into a JSON list."},
                {"role": "user", "content": content}
            ],
            temperature=0
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(json.dumps({"error": f"OCR Processing Failed: {str(e)}"}))

if __name__ == "__main__":
    main()
