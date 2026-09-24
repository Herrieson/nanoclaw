import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Objective verification whitelist data
HARDCODED_DATA = {
    "101": {"systolic": 110, "diastolic": 70, "consent_signed": "Yes"},
    "102": {"systolic": 142, "diastolic": 80, "consent_signed": "Yes"},
    "103": {"systolic": 120, "diastolic": 92, "consent_signed": "Yes"},
    "104": {"systolic": 115, "diastolic": 75, "consent_signed": "No"},
    "105": {"systolic": 118, "diastolic": 78, "consent_signed": "Yes"},
    "106": {"systolic": 125, "diastolic": 80, "consent_signed": "Yes"},
    "107": {"systolic": 139, "diastolic": 89, "consent_signed": "Yes"},
    "108": {"systolic": 150, "diastolic": 95, "consent_signed": "No"},
    "109": {"systolic": 110, "diastolic": 70, "consent_signed": "Yes"},
    "110": {"systolic": 100, "diastolic": 60, "consent_signed": "Yes"}
}

def smart_mock(patient_id):
    if not patient_id:
        return json.dumps({"error": "Missing patient_id parameter. Usage: python cloud_vitals_api.py <patient_id>"})
    
    if patient_id in HARDCODED_DATA:
        return json.dumps({"status": "success", "data": HARDCODED_DATA[patient_id]})
    
    # LLM-as-a-Mock for unexpected patient IDs (Enhances robustness)
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
                {"role": "system", "content": "You are a virtual health database API. Given a patient ID, return a JSON string with keys: 'systolic' (int), 'diastolic' (int), and 'consent_signed' ('Yes' or 'No'). Make up realistic values."},
                {"role": "user", "content": f"Patient ID: {patient_id}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": f"Connection failed. {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing patient_id parameter. Usage: python cloud_vitals_api.py <patient_id>"}))
        sys.exit(1)
    
    print(smart_mock(sys.argv[1].strip()))
