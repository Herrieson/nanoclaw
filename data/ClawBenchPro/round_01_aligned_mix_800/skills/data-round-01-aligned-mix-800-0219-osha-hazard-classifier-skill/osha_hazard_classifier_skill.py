import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

http_client = httpx.Client(verify=False)

try:
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
except:
    client = None

def classify_hazard(observation):
    if not observation:
        return "Error: Missing observation parameter."
    
    if not client:
        # Fallback for local debugging if OpenAI client fails to init
        obs_lower = observation.lower()
        if "scaffolding" in obs_lower or "wire" in obs_lower:
            return "SEVERITY: CRITICAL HAZARD"
        return "SEVERITY: MINOR"

    system_prompt = """You are the official OSHA City Compliance checking API.
Analyze the given construction site observation and classify its severity.
Rules:
1. Missing guardrails on scaffolding -> CRITICAL
2. Exposed live wires -> IMMEDIATE / CRITICAL
3. Not wearing dust masks during dry sweep -> MINOR
4. Hard hats left off during break near inactive crane -> MINOR
Respond strictly in this format: 
SEVERITY: [CRITICAL | IMMEDIATE | MINOR | COMPLIANT]
REASON: [Brief explanation]"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Observation to evaluate: {observation}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: API Connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python osha_hazard_classifier_skill.py '<observation_text>'")
        sys.exit(1)
        
    print(classify_hazard(sys.argv[1]))
