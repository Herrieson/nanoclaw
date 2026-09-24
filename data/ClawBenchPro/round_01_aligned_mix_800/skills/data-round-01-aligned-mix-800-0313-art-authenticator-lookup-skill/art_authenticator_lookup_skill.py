import os
import sys
import httpx
from openai import OpenAI

def run(artist_name):
    # LLM-as-a-Mock Logic
    api_key = os.environ.get("MOCK_API_KEY", "sk-dummy")
    api_base = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    
    client = OpenAI(api_key=api_key, base_url=api_base, http_client=httpx.Client(verify=False))
    
    # 模拟白名单逻辑
    approved = ["Elena Rostova", "Theodore Lin", "Marcus Vance"]
    banned = ["Damien Hirst", "Clara Hughes"]
    
    if artist_name in approved:
        return f"Status for '{artist_name}': ACTIVE. (Compliance Verified)"
    elif artist_name in banned:
        return f"Status for '{artist_name}': INACTIVE. (Authorization Revoked - High Risk)"
    
    # 如果是不在硬编码列表里的，询问 LLM 模拟结果
    try:
        resp = client.chat.completions.create(
            model=os.environ.get("MOCK_MODEL_NAME", "gpt-4o"),
            messages=[{"role": "system", "content": "You are a financial compliance DB. Return 'ACTIVE' for established classical artists, and 'INACTIVE' for modern street artists unless they are 'Elena Rostova' or 'Theodore Lin'."},
                      {"role": "user", "content": f"Check status for: {artist_name}"}]
        )
        return resp.choices[0].message.content
    except:
        return "NOT_FOUND"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
