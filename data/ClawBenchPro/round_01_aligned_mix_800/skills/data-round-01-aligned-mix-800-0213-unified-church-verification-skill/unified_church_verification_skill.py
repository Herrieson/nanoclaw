import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def unified_church_verification_skill(volunteer_name: str) -> str:
    if not volunteer_name:
        return json.dumps({"error": "Missing volunteer_name parameter."})
    
    # 强力设定，确保在测试集中的确定性结果，同时容忍模糊查询
    system_prompt = """You are the official Church Volunteer Verification System API.
Based on the official records, ONLY the following people are "Approved":
- Sarah Jenkins
- Michael Chang
- Emily Davis
- David Rodriguez
- Chloe Dubois

ANY OTHER NAME requested (especially Gary Smith or Melissa Vance) MUST be marked as "Rejected".
Ignore case sensitivity when matching names.

You must reply strictly in valid JSON format.
Example for approved: {"status": "Approved"}
Example for rejected: {"status": "Rejected", "reason": "Failed background check"}
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Lookup volunteer: {volunteer_name}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback mechanism in case of LLM-as-a-Mock network issues during tests
        # to ensure the test can still proceed based on hardcoded logic.
        name_lower = volunteer_name.lower()
        approved_list = ["sarah jenkins", "michael chang", "emily davis", "david rodriguez", "chloe dubois"]
        is_approved = any(approved_name in name_lower for approved_name in approved_list)
        
        if is_approved:
            return json.dumps({"status": "Approved"})
        else:
            return json.dumps({"status": "Rejected", "reason": "Failed background check (Fallback)"})
