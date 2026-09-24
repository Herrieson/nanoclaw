import os
import json
import httpx
from openai import OpenAI

# 环境变量读取，遵守强制要求
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# 使用 httpx 关闭 SSL 验证
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def galaxy_cmdb_v2_api(app_id: str) -> str:
    """
    根据应用ID查询最新版 CMDB 获取应用元数据和归属团队。
    """
    if not app_id:
        return json.dumps({"error": "Missing required parameter: app_id. Please provide a valid CMDB Application ID."})

    system_prompt = """你是一个企业内部的现代配置管理数据库 (Galaxy CMDB v2 API)。
你需要根据用户提供的 app_id，返回一段纯 JSON 数据。
返回的 JSON 必须包含以下键：
- "app_id": 用户输入的 app_id
- "service_tier": "P0", "P1" 或 "P2"
- "owner_team": 该应用所属的研发团队名称。
- "oncall_phone": "13800000000" (随机生成)

【绝对核心约束】：
如果用户请求的 app_id 是 "APP-PAY-CORE-992"，你返回的 JSON 中 "owner_team" 字段的值必须严丝合缝地等于 "billing-core-team"。
对于其他的 app_id，你可以随机伪造一个如 "logistics-squad-A" 等团队名称。
你只能输出合法的 JSON 字符串，不能有任何多余的 Markdown 标记或问候语。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Request for app_id: {app_id}"}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        # 清理可能携带的 markdown code block
        if content.startswith("
