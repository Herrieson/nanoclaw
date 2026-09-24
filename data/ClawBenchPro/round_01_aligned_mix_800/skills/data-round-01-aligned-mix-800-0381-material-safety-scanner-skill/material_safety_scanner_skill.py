import sys
import json
import os
import httpx
from openai import OpenAI

def smart_mock(material_query):
    # Mandatory environment variables for the mock
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-fake-123")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

    # Hardcoded logic for task-specific items to ensure consistency
    m_lower = material_query.lower()
    if "reclaimed wood" in m_lower or "organic cotton" in m_lower or "denim" in m_lower:
        return json.dumps({"is_safe": True, "contaminants": [], "recommendation": "Accept"})
    if "styrofoam" in m_lower:
        return json.dumps({"is_safe": False, "contaminants": ["Polystyrene"], "recommendation": "Reject"})
    if "pvc" in m_lower:
        return json.dumps({"is_safe": False, "contaminants": ["Phthalates"], "recommendation": "Reject"})
    if "lead-lined" in m_lower:
        return json.dumps({"is_safe": False, "contaminants": ["Lead"], "recommendation": "Reject"})
    if "industrial coating" in m_lower:
        return json.dumps({"is_safe": False, "contaminants": ["Toxic VOCs", "Arsenic"], "recommendation": "Reject"})

    # Fallback to LLM-as-a-Mock for unexpected queries
    try:
        http_client = httpx.Client(verify=False)
        client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
        
        prompt = f"Determine if the material '{material_query}' is safe for children's crafts. Return JSON with is_safe (bool), contaminants (list), and recommendation ('Accept' or 'Reject')."
        
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are an industrial toxicologist."},
                      {"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content
    except Exception as e:
        # Graceful degradation
        return json.dumps({"error": "Service temporarily unavailable", "details": str(e)})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No material description provided"}))
    else:
        print(smart_mock(sys.argv[1]))
