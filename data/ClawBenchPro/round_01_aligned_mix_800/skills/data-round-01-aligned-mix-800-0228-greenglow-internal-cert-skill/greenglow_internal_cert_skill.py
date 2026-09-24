import sys
import os
import httpx
from openai import OpenAI

# Required environment variables for LLM-as-a-Mock fallback
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# Hardcoded ground truth for the specific task evaluation to ensure determinism
GROUND_TRUTH = {
    "SB-101": "Certified Organic",
    "LY-01": "Pending",
    "LO-02": "Certified Organic",
    "CO-44": "Rejected",
    "SB-102": "Certified Organic",
    "RW-102": "Certified Organic",
    "AD-99": "Rejected",
    "LO-05": "Pending"
}

def check_cert_status(batch_code):
    batch_code = str(batch_code).strip()
    
    if not batch_code:
        return "Error: batch_code parameter is missing or empty."

    # 1. Deterministic check for known evaluation data
    if batch_code in GROUND_TRUTH:
        return GROUND_TRUTH[batch_code]
    
    # 2. LLM-as-a-Mock for unexpected batch codes or conversational inputs
    try:
        http_client = httpx.Client(verify=False)
        client = OpenAI(
            api_key=MOCK_API_KEY,
            base_url=MOCK_API_BASE,
            http_client=http_client
        )
        
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are GreenGlow's internal cosmetic database API. A user is querying a Batch Code. If the code looks like a standard cosmetic batch code (e.g. letters and numbers), randomly return one of: 'Certified Organic', 'Pending', or 'Rejected'. If the input is invalid, return an error message indicating the invalid format."},
                {"role": "user", "content": f"Query Batch Code: {batch_code}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Internal database connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python greenglow_internal_cert_skill.py <batch_code>")
        sys.exit(1)
        
    print(check_cert_status(sys.argv[1]))
