import os
import json
import httpx
from openai import OpenAI

def analyze_poetry(text):
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-poetry-123")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

    prompt = f"""
    You are a professional literary critic. Analyze the following poem draft. 
    1. Identify the core title.
    2. Count only the valid poetic lines (ignore tags like <<<ERR>>> or random notes).
    3. Return a JSON only: {{"official_title": "...", "valid_lines": int, "sentiment": "..."}}

    Poem text:
    {text}
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(analyze_poetry(sys.argv[1]))
