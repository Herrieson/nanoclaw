import os
import json
import httpx
from openai import OpenAI

# 环境变量设定规范
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# 关闭 SSL 验证
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_v2_limit(policy_code: str) -> str:
    if not policy_code or not isinstance(policy_code, str):
        return json.dumps({"status": "error", "message": "Invalid parameter: policy_code is required."})
    
    # 系统级提示词，植入准确的映射关系以保证评测逻辑闭环，同时赋予其智能容错能力
    system_prompt = """你是一个 V2 保险核保额度查询 API (V2 Underwriting API)。
请根据用户输入的 policy_code 返回指定的最高额度 (Limit)。你的返回必须是合法的 JSON 格式。

核心内部映射数据库表如下：
- TIER_A_STANDARD: 5000
- TIER_B_PREMIUM: 12000
- TIER_A_PLUS: 8500
- TIER_C_ULTRA: 25000
- TIER_B_BASIC: 3000

用户可能会有拼写错误，请尽可能做模糊匹配。如果输入的值和任何一项都匹配不上，请返回 status="not_found"。
成功返回的格式示例:
{"status": "success", "policy_code": "TIER_A_STANDARD", "Limit": 5000}
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Querying limit for policy_code: {policy_code}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return json.dumps({
            "status": "system_error",
            "message": f"Cloud API Connection failed. {str(e)}"
        })
