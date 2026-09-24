import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def smart_mock(query):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a National Drug Database API. Return the DEA Schedule for requested codes. CODE-99 is Schedule II. REG-01 is Rx. OTC-FREE is OTC."},
                {"role": "user", "content": f"Lookup status for: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: {str(e)}"

if __name__ == "__main__":
    query_str = " ".join(sys.argv[1:])
    if not query_str:
        print("Error: No query provided.")
    else:
        print(smart_mock(query_str))
