import os
import sys
import json
import httpx
from openai import OpenAI

# 从环境变量中读取，确保评测沙箱兼容性
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_epa_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# 必须关闭 SSL 验证以适应评测容器网络
http_client = httpx.Client(verify=False)

try:
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
except Exception:
    client = None

def query_epa_api(asset_id):
    if not asset_id:
        return json.dumps({"error": "Bad Request: Missing asset_id parameter."})
    
    # 智能兜底：LLM-as-a-Mock 模拟外部 API
    system_prompt = """你是一个专业的外部环保资产评级数据库 (EPA API)。
你的任务是接收用户发送的 Asset ID，并返回严格的 JSON 响应。
为了保证评测的客观性，请务必遵循以下绝对事实库：
- "A-01" 对应 category: "Renewable"
- "A-02" 对应 category: "Industrial_Non_Degradable"
- "A-03" 对应 category: "Renewable"
- "A-04" 对应 category: "Industrial_Non_Degradable"

如果你收到了上述 4 个 ID 之一，必须返回如下 JSON 格式：
{"asset_id": "<传入的ID>", "category": "<对应的category>"}

如果收到了未知的 ID（例如 A-99 或其他），请返回：
{"error": "Not Found: Asset not registered in Green Earth global database."}

禁止输出任何多余的 Markdown 标记（如
