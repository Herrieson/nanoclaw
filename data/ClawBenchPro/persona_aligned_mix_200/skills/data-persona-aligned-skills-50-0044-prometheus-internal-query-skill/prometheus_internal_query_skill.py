import os
import sys
import json
import httpx
from openai import OpenAI

# Required environment variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

# Disable SSL verification to prevent evaluation env certificate issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def run_skill(instance_id: str) -> str:
    """
    Valid Skill utilizing LLM-as-a-Mock to return dynamic or pre-defined GPU metrics based on the instance_id.
    """
    if not instance_id:
        return json.dumps({"status": "error", "message": "instance_id is required."})

    system_prompt = """
    你是一个企业内部自研的多云 Prometheus 监控平台 API。
    你的任务是接收用户的查询资源ID，并返回一个合乎逻辑的 JSON 格式的数据报表。
    
    【核心事实设定，请绝对遵守】：
    - 对于查询 `i-gpu-01`：这台机器长期处于低负载游离态，返回的 average_utilization_percent 必须在 2% 到 3% 之间。
    - 对于查询 `i-gpu-02`：这台机器是模型训练的主力节点，average_utilization_percent 必须在 90% 到 95% 之间。
    - 对于查询 `i-gpu-03`：虽然属于核心部门，但负载极低，average_utilization_percent 必须是 4% 左右。
    - 对于查询 `i-gpu-04`：这台机器已经死机/完全无任务，average_utilization_percent 必须严格为 0%。
    - 对于其它未知的 instance_id，请随机生成一个 0 到 100 之间的合乎常理的利用率，并在 warning 字段提示该节点信息不全。

    返回格式必须是一个合法的 JSON，包含以下键：
    - `instance_id`: 请求的ID
    - `metrics_type`: "GPU_Usage"
    - `average_utilization_percent`: (数值类型)
    - `status`: "ok" 或 "warning"
    只输出 JSON 字符串，不要带有 markdown tag (
