import json
import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

def validate_eco_standard(total_weight, recycled_weight):
    # Core logic: Base 15% check + Dynamic "Coefficient" Mock via LLM
    try:
        client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))
        
        # We use LLM to simulate a complex regulatory calculation
        prompt = f"A chemical batch has total weight {total_weight} and recycled weight {recycled_weight}. The standard threshold is 15%. Apply a compensation coefficient of 1.0 (standard). Is it compliant? Return JSON only: {{\"is_compliant\": bool, \"percentage\": float}}"
        
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception:
        # Fallback to simple logic if LLM-Mock fails
        percentage = (recycled_weight / total_weight) * 100
        return json.dumps({"is_compliant": percentage >= 15.0, "percentage": percentage})

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        print(validate_eco_standard(float(sys.argv[1]), float(sys.argv[2])))
