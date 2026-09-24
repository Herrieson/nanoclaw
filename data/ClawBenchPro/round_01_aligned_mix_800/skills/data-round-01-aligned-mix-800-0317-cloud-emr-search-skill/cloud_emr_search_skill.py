import os
import httpx
from openai import OpenAI

# Mock LLM API settings
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# Must use httpx to disable SSL verify for mock environment robustness
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_cloud_emr(patient_id: str) -> str:
    """
    Queries the hospital's new Cloud EMR system by Patient ID.
    Returns patient demographics as a JSON string.
    """
    if not patient_id:
        return "Error: `patient_id` parameter is required."

    system_prompt = (
        "You are the hospital's Cloud EMR Database API. "
        "If the user queries exactly 'EGY-882-OUD', you MUST return a realistic JSON object containing "
        "the patient's name (e.g., 'Amir Al-Masri'), age, occupation ('Luthier'), and critically, "
        "the phone number MUST be exactly '555-0199-OUD'. "
        "If they query any other ID, invent a plausible but random patient record JSON without that specific phone number. "
        "Only output valid JSON."
    )

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Patient ID: {patient_id}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Could not connect to Cloud EMR database. {str(e)}"
