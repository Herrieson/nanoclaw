import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def run(student_data):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a Legal Compliance AI. Evaluate if the following student record has a liability risk. If status is not 'Signed', return 'RISK_DETECTED'."},
                {"role": "user", "content": f"Data: {student_data}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Cloud Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
