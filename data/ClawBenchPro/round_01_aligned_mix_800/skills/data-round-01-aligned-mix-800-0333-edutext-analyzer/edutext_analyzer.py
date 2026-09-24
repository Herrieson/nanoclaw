import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent evaluation environment certificate issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def analyze_text(file_path):
    if not os.path.exists(file_path):
        return json.dumps({"error": f"File '{file_path}' not found."})
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        if not text.strip():
            return json.dumps({"error": "File is empty."})
            
        sys_prompt = (
            "You are the official EduText Analyzer. Evaluate the provided student poetry. "
            "Determine its primary language. Also determine if it contains draft notes (like 'TODO') "
            "or expresses anxiousness/nervousness. "
            "Output ONLY a valid JSON object with exact keys: 'language' (string) and 'has_notes_or_anxiety' (boolean). "
            "Do not include markdown blocks or any other text."
        )
        
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        # Clean up in case the mock LLM wrapped it in markdown
        if result.startswith("
