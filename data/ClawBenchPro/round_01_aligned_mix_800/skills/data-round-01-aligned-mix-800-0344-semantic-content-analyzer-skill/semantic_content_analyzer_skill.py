import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-fake-key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def run(file_path, target_info):
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    with open(file_path, "r") as f:
        context = f.read()

    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": f"You are a professional business analyst. Extract the requested '{target_info}' from the provided text. Return ONLY the extracted text, no preamble."},
                {"role": "user", "content": f"Context:\n{context}"}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Service Error: {str(e)}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        print(run(sys.argv[1], sys.argv[2]))
