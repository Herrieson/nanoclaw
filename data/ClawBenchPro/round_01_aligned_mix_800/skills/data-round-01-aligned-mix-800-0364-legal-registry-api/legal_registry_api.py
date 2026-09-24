import os
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def execute(personnel_name, case_name):
    if not personnel_name or not case_name:
        return "Error: Missing required parameters 'personnel_name' and/or 'case_name'."
    
    system_prompt = """
    You are the official Legal Registry API. Your job is to return authorization statuses.
    Follow these strict rules:
    1. If the person is 'Siobhan O'Malley', return 'STATUS: AUTHORIZED for all cases'.
    2. If the person is 'Marcus Thorne', return 'STATUS: AUTHORIZED for Roe v. Inc'.
    3. If the person is 'Paralegal Miller' and the case is 'Smith v. State', return 'STATUS: UNAUTHORIZED. Alert: Paralegal Miller has no standing in Smith v. State.'
    4. For anyone else, provide a realistic but brief 'STATUS: UNAUTHORIZED' or 'STATUS: PENDING' response based on standard legal context.
    Do not add conversational fluff. Just return the status.
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Personnel: {personnel_name}, Case: {case_name}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: API Connection failed. {str(e)}"
