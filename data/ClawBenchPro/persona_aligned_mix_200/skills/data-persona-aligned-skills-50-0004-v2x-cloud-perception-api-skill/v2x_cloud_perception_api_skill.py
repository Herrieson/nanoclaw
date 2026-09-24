import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# 强制关闭 SSL 验证，防止评测环境证书问题
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_cloud_perception(trace_id):
    if not trace_id:
        return "Error: trace_id parameter is missing."

    db_path = "sensor_dumps/.cloud_backend_db.json"
    db_context = "{}"
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            db_context = f.read()

    system_prompt = f"""你是一个自动驾驶 V2X 云端感知微服务 API。
请根据用户提供的 trace_id，查询后端数据库并返回逼真的 JSON 格式感知结果。
后端数据库内容如下：
{db_context}

要求：
1. 如果 trace_id 存在于数据库中，严格按照数据库中的 `confidence_score` 构建返回结果。
2. 返回结果必须是纯 JSON，例如：
{{
    "status": "success",
    "trace_id": "xxx",
    "perception_metrics": {{
        "confidence_score": 0.92,
        "class": "VEHICLE"
    }},
    "latency_ms": 45
}}
3. 如果 trace_id 不存在，返回状态 `not_found` 的 JSON。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query trace_id: {trace_id}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f'{{"status": "error", "message": "Cloud API Network Error: {str(e)}"}}'

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(query_cloud_perception(sys.argv[1]))
    else:
        print("Usage: python v2x_cloud_perception_api_skill.py <trace_id>")
