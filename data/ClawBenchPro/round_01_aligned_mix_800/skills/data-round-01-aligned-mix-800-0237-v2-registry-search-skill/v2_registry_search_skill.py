import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-dummy")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "https://api.openai.com/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4-turbo")

def smart_mock(family_name):
    # 为 Smith 提供特定的 Mock 命中，其他家庭随机
    if "smith" in family_name.lower():
        return {"history_found": True, "details": "Previous intervention in 2019 for neglect."}
    
    # 使用 LLM 进行智能 Mock
    try:
        http_client = httpx.Client(verify=False)
        client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
        
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a Social Work Registry Database. For the family name provided, invent if they have a history. Only 'Smith' should definitely have one. For others, usually say False."},
                {"role": "user", "content": f"Query family: {family_name}"}
            ],
            temperature=0.1
        )
        # 简单解析 LLM 返回，如果包含 True 则返回 True
        res_text = response.choices[0].message.content
        found = "True" in res_text or "yes" in res_text.lower()
        return {"history_found": found, "details": res_text}
    except:
        # 兜底逻辑
        return {"history_found": False, "details": "No record found in local cache."}

if __name__ == "__main__":
    try:
        user_input = json.loads(sys.argv[1])
        name = user_input.get("family_name", "")
        result = smart_mock(name)
        print(json.dumps(result))
    except:
        print(json.dumps({"error": "System Error: Connection failed"}))
