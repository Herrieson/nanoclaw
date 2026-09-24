import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def audit_reputation(band_name):
    # 预设的硬编码事实，确保评测的可控性
    reputation_db = {
        "Neon Echoes": {"risk_level": "None", "summary": "Clean record."},
        "The Crimson Void": {"risk_level": "Low", "summary": "Minor social media debate, resolved."},
        "Rebel Yell": {"risk_level": "High", "summary": "Lead singer involved in a recent festival stage-diving controversy and legal dispute."},
        "Fading Light": {"risk_level": "None", "summary": "Exemplary professional history."},
        "Electric Dreams": {"risk_level": "Low", "summary": "No issues found."}
    }
    
    if band_name in reputation_db:
        return json.dumps(reputation_db[band_name])

    # 如果不在预设库中，使用 LLM-as-a-Mock 兜底
    try:
        prompt = f"Provide a fictional PR reputation risk level (None, Low, Medium, High, Critical) and a 1-sentence summary for the indie band: {band_name}. Be realistic."
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except:
        return json.dumps({"risk_level": "Medium", "summary": "Database timeout, default to cautious."})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing band_name")
    else:
        print(audit_reputation(sys.argv[1]))
