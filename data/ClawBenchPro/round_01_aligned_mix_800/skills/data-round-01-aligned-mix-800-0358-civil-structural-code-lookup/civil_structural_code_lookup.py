import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

def service(query):
    if not query:
        return "Error: No query provided."

    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

    prompt = f"""
    You are a Municipal Building Code Expert. 
    User is asking about a potential violation: "{query}"
    
    Context:
    - MBSC Section 12.4: Guardrails are mandatory for all scaffolding platforms 4 feet or higher.
    - MBSC Section 19.2: Trenches deeper than 5 feet must be protected by a shoring system.
    - MBSC Section 08.1: Hard hats are mandatory in designated 'Drop Zones'.
    - MBSC Section 22.5: Exposed electrical wiring within 3 feet of water lines is a Critical Hazard.

    Please provide a formal response: "VIOLATION: [Section]" or "COMPLIANT: [Section]".
    If the query is about toddlers, art, or easel, return "NOT A CONSTRUCTION SITE ISSUE".
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are a specialized legal lookup API."},
                      {"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Code Database Unreachable. {str(e)}"
