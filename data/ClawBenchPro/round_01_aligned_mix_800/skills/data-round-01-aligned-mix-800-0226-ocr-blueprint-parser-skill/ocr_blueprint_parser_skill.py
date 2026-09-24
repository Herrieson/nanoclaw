import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def ocr_mock(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    with open(file_path, 'r') as f:
        raw_content = f.read()

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a specialized Woodworking OCR tool. Extract items and dimensions from the provided raw text data which simulates a scanned PDF."},
                {"role": "user", "content": f"Extract data from: {raw_content}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OCR Engine Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(ocr_mock(sys.argv[1]))
