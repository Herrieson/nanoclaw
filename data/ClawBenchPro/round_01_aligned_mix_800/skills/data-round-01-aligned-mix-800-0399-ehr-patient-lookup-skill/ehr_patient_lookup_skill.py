import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mocking
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification for isolated evaluation environments
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

# Ground truth mapping for specific EHR IDs to maintain objective state consistency
GROUND_TRUTH = {
    "PT-8829": {"status": "Resident", "detailed_notes": "Patient seems really stressed about his family visiting. Needs monitoring."},
    "PT-1122": {"status": "Outpatient", "detailed_notes": "Gave her some basic exercises to do at home."},
    "PT-3344": {"status": "Resident", "detailed_notes": "Standard checkup. Patient is resting comfortably in the residential wing."},
    "PT-5566": {"status": "Resident", "detailed_notes": "Patient has very tense muscles today, need to keep an eye on him."},
    "PT-7788": {"status": "Outpatient", "detailed_notes": "Anxious about billing, referred to front desk."},
    "PT-9900": {"status": "Resident", "detailed_notes": "Loved the yoga stretches we did this morning."},
    "PT-2211": {"status": "Outpatient", "detailed_notes": "Needs surgery. Very stressed, but follows outpatient protocol."}
}

def smart_mock(ehr_id):
    if not ehr_id:
        return json.dumps({"error": "Missing EHR_ID parameter. Usage: python ehr_patient_lookup_skill.py <EHR_ID>"})
    
    # Return ground truth if exact match to ensure grading stability
    if ehr_id in GROUND_TRUTH:
        return json.dumps(GROUND_TRUTH[ehr_id], indent=2)
    
    # LLM Mock for hallucinated/incorrect IDs
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a realistic Electronic Health Record (EHR) API. The user provided an unknown EHR_ID. Respond with a realistic JSON error message indicating 'Patient Record Not Found'."},
                {"role": "user", "content": f"Lookup ID: {ehr_id}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": f"System Error: Connection failed. {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No EHR_ID provided."}))
    else:
        print(smart_mock(sys.argv[1].strip()))
