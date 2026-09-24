import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_diet_mock(diagnosis):
    if not diagnosis:
        return "Error: Missing required parameter 'diagnosis'. Please check the skill documentation."
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a hospital dietary mapping API. Your job is to strictly map the provided medical diagnosis to one of the following exact dietary restriction labels: 'Diabetic', 'Soft Foods', 'Peanut Allergy', 'Low Sodium', 'Gluten Free'. If the diagnosis implies no dietary restriction (e.g., 'Healthy', 'None', 'Broken Arm'), reply exactly with 'None'. Do not output any conversational text, only the label."},
                {"role": "user", "content": f"Diagnosis: {diagnosis}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: API Connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing parameter 'diagnosis'. Usage: python3 hospital_diet_v2_skill.py <diagnosis>")
    else:
        diag = sys.argv[1]
        print(smart_diet_mock(diag))
