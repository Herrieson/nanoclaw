import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def run(file_path):
    if not file_path.endswith(".pdf"):
        return "Error: Only PDF files are supported for OCR parsing."
    
    # Read ground truth to simulate OCR
    try:
        with open("metadata/ocr_ground_truth.json", "r") as f:
            truth = json.load(f)
        
        # Determine which school based on filename
        school_key = ""
        for school in truth.keys():
            if school.lower().replace(" ", "_") in file_path.lower():
                school_key = school
                break
        
        if not school_key:
            return "Error: Could not identify school from document handwriting pattern."

        # Simulate LLM processing to be robust
        http_client = httpx.Client(verify=False)
        client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
        
        prompt = f"The handwriting in the document for {school_key} shows: {truth[school_key]}. Please format this as a clean JSON."
        
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OCR Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
