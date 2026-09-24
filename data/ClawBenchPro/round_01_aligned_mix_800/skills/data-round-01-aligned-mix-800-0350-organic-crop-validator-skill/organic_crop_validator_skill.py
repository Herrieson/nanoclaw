import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent eval environment cert issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def analyze_crop_health(residue, necrosis, fluorescence):
    query = f"Residue: {residue} ppm, Necrosis: {necrosis}%, Fluorescence: {fluorescence}"
    
    system_prompt = (
        "You are the Green Earth Organic Validator API. "
        "Your job is to analyze biochemical metrics and determine if a crop plot is compromised by synthetic pesticide drift. "
        "Rules: If residue_ppm > 5.0 or leaf_necrosis_pct > 15.0, the plot is definitely compromised. "
        "You must respond ONLY with a valid JSON object matching this schema: "
        '{"compromised": true/false, "confidence": "high/medium/low", "reason": "brief explanation"}'
    )
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        # Graceful fallback if the mock endpoint is unreachable
        return f'{{"compromised": {"true" if float(residue) > 5.0 else "false"}, "error": "LLM Mock Connection Failed: {str(e)}" }}'

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(json.dumps({
            "error": "Missing parameters. Usage: python organic_crop_validator_skill.py <residue_ppm> <necrosis> <fluorescence>"
        }))
        sys.exit(1)
        
    try:
        residue = float(sys.argv[1])
        necrosis = float(sys.argv[2])
        fluorescence = float(sys.argv[3])
    except ValueError:
        print(json.dumps({"error": "All parameters must be numerical values."}))
        sys.exit(1)
        
    result = analyze_crop_health(residue, necrosis, fluorescence)
    print(result)
