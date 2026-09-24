import os
import sys
import json
import httpx
from openai import OpenAI

# 必须约定这三个环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 必须使用 httpx 关闭 SSL 验证，防止评测环境证书问题
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

KNOWN_PRICES = {
    "BIM-PRO": 4500,
    "BIM-TRIAL": 900,
    "BIM-ENT": 15000,
    "BIM-STD": 2500,
    "BIM-UPG": 1200,
    "BIM-EDU": 800,
    "BIM-RENEW": 3000,
    "BIM-SITE": 5000
}

def smart_mock(license_code):
    if not license_code:
        return json.dumps({"status": "error", "message": "Missing required parameter: license_code"})
    
    # 1. Deterministic check for exact matches to guarantee stable objective evaluation math
    clean_code = license_code.strip().upper()
    if clean_code in KNOWN_PRICES:
        return json.dumps({
            "status": "success",
            "license_code": clean_code,
            "price_usd": KNOWN_PRICES[clean_code]
        })
    
    # 2. Smart fallback using LLM-as-a-Mock for robust error handling and fuzzy matching
    try:
        system_prompt = f"""You are the backend logic for the 'BIM Cloud Pricer API'.
The user passed a malformed or unknown license code: '{license_code}'.
Try to extract the core license string and map it to the known database: {json.dumps(KNOWN_PRICES)}.
If it closely matches one, return the exact JSON format: {{"status": "success", "license_code": "MATCHED_CODE", "price_usd": PRICE}}.
If it is completely unrelated, return a realistic JSON API error."""

        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Resolve license code: {license_code}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Cloud API Connection failed: {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Missing required parameter: license_code. Usage: python bim_cloud_pricer_api.py <license_code>"}))
        sys.exit(1)
        
    user_input = sys.argv[1]
    result = smart_mock(user_input)
    print(result)
