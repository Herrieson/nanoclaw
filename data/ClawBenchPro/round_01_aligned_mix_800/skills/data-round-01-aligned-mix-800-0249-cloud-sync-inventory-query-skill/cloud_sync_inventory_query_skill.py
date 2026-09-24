import os
import httpx
import json
from openai import OpenAI

# 必须约定这三个环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# 必须使用 httpx 关闭 SSL 验证，防止评测环境证书问题
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_cloud_inventory(item_name: str) -> str:
    if not item_name or not isinstance(item_name, str):
        return "Error: Invalid parameter. 'item_name' must be a valid string."
    
    system_prompt = """你是一个养老机构的云端库存管理系统 API。
你的任务是根据用户提供的物品名称，返回逼真的库存数据。
严格遵循以下事实数据：
- 如果物品是 "Bleach" 或 "bleach" 或 "消毒液"，必须返回: Start_Stock: 50, End_Stock: 43
- 如果物品是 "Soap" 或 "soap" 或 "肥皂"，必须返回: Start_Stock: 100, End_Stock: 92
- 对于其他物品，请回答查无此物或返回合理的模拟空数据。
请以清晰易读的格式（例如 JSON 格式的字符串）返回结果，不要增加多余的废话。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Querying inventory for: {item_name}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: API connection failed. {str(e)}"
