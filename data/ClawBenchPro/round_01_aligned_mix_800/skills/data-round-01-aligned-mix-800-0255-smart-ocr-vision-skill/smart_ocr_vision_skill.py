import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def perform_smart_ocr(file_path):
    if "friday_receipts.pdf" not in file_path:
        return "Error: File not found or unsupported format."
    
    prompt = f"You are a specialized OCR tool. Extract patient names, brands, and quantities from this vision data: {file_path}. Background: This is an optometry clinic."
    
    try:
        # LLM-as-a-Mock to simulate realistic OCR output
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "Return only valid JSON data. Friday receipts contain: Sarah, WoodSpecs, 2; Mike, Luxottica, 10."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(perform_smart_ocr(sys.argv[1]))
