import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def service(query):
    # Use LLM-as-a-Mock to handle search queries
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=httpx.Client(verify=False)
    )
    
    prompt = f"""
    You are the Internal Pharmacy Database. Return the drug name for the following NDC code:
    - NDC-001: Amoxicillin
    - NDC-002: Oxycodone
    - NDC-003: Lisinopril
    - NDC-004: Adderall
    - NDC-005: Diazepam
    - NDC-006: Ibuprofen
    
    User Query: {query}
    Return only the Drug Name or 'Not Found'.
    """
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Database Error: {str(e)}"
