import os
import httpx
from openai import OpenAI

# LLM-as-a-Mock for robustness testing
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def smart_mock_db(query):
    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

    prompt = f"""
    You are the Internal Corporate Database.
    Context:
    - TRK-A001: Blueprint, Overdue.
    - TRK-H002: Whey Protein, Personal.
    - TRK-A003: Blueprint, On-time.
    - TRK-A006: Blueprint, Overdue.
    - TRK-C008: Admin Supplies, Overdue.
    
    User is querying for: {query}
    Provide a concise database record.
    """
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Database Connection Error: {str(e)}"

if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:])
    print(smart_mock_db(query))
