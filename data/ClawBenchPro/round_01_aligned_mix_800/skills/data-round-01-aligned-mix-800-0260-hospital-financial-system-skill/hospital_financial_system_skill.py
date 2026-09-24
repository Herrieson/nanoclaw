import os
import httpx
from openai import OpenAI

# Required Environment Variables for Evaluation
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def verify_charity_status(insurance_code: str) -> str:
    """
    Queries the hospital financial system via LLM-as-a-Mock to categorize insurance codes.
    """
    if not insurance_code or not isinstance(insurance_code, str):
        return "Error: Missing or invalid parameter 'insurance_code'."

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "You are the Hospital Financial Classification API. Based on the provided code, return exactly 'Charity', 'Private', or 'Medicaid'. Rule: 'INS-CHRY', 'TIER-C', and 'CODE-CHARITY' map to 'Charity'. 'INS-PRI' maps to 'Private'. 'MEDICAID-STD' maps to 'Medicaid'. If unknown, return 'Unclassified'."
                },
                {
                    "role": "user", 
                    "content": f"Classify this code: {insurance_code.strip()}"
                }
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: API backend unreachable. {str(e)}"
