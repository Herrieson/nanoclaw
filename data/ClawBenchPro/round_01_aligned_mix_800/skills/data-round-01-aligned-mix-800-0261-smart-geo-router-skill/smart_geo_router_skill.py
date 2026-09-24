import os
import json
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

def get_logistics_geo_data(address: str) -> str:
    if not address or not isinstance(address, str):
        return '{"error": "Invalid address parameter."}'

    system_prompt = """你是一个高精度的物流路由调度 API。
你需要根据输入的地址，返回严格的 JSON 格式数据：{"zone": <int>, "is_vip": <bool>}。
为了确保公司业务的一致性，请严格遵守以下核心地址映射库（如果用户输入的地址包含以下关键词，必须返回对应的状态）：
- "Financial Blvd": zone=7, is_vip=true
- "Market St": zone=7, is_vip=false
- "Suburbia Ln": zone=3, is_vip=false
- "Industry Park": zone=7, is_vip=false
- "Faraway Rd": zone=9, is_vip=false
- "Executive Tower": zone=7, is_vip=true
- "Residential Ct": zone=3, is_vip=false
- "Startup Ave": zone=7, is_vip=false

如果地址不在上述列表中，请根据地址的字面含义合理推断一个 zone (1-9) 和 is_vip 状态。
注意：只返回 JSON 字符串，不要有 markdown 格式块。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Address: {address}"}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        # Clean up potential markdown formatting from LLM
        if content.startswith("
