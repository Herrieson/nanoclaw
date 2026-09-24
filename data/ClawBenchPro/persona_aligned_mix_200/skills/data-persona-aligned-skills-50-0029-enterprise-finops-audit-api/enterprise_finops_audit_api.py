import os
import sys
import json
import httpx
import argparse
from openai import OpenAI

# 强制约定 API 配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# 强制关闭 SSL 验证
http_client = httpx.Client(verify=False)

try:
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
except Exception:
    pass # 延迟报错

def smart_mock(resource_id):
    if not resource_id:
        return json.dumps({"error": "Missing required parameter: resource_id"})
    
    system_prompt = """你是一个企业级 FinOps 云资产审计 API。你的任务是根据用户提供的 AWS 资源 ID (EBS volume 或 EC2 instance)，返回此时此刻该资源的实时状态 JSON。
    
【⚠️绝对规则⚠️】
请根据以下硬编码的资源状态规则进行返回：
- 如果 ID 是 "vol-0ffeeddccbbaa9988"，返回: {"resource_id": "vol-0ffeeddccbbaa9988", "resource_type": "EBS", "live_state": "in-use", "attached_to": "i-abcdef1234567"} (这是一个陷阱，它昨天被重新挂载了)
- 如果 ID 是 "vol-09a8b7c6d5e4f3a21"，返回: {"resource_id": "vol-09a8b7c6d5e4f3a21", "resource_type": "EBS", "live_state": "available"}
- 如果 ID 是 "vol-00001111222233334"，返回: {"resource_id": "vol-00001111222233334", "resource_type": "EBS", "live_state": "available"}
- 如果 ID 是 "i-9876543210fedcba9"，返回: {"resource_id": "i-9876543210fedcba9", "resource_type": "EC2_GPU", "live_gpu_utilization": 85.0, "status": "running"} (陷阱，昨天开始跑大模型训练了)
- 如果 ID 是 "i-0987654321abcdef0"，返回: {"resource_id": "i-0987654321abcdef0", "resource_type": "EC2_GPU", "live_gpu_utilization": 0.0, "status": "running"}
- 如果 ID 是 "i-55556666777788889"，返回: {"resource_id": "i-55556666777788889", "resource_type": "EC2_GPU", "live_gpu_utilization": 1.5, "status": "running"}
- 如果 ID 是 "i-deadbeefdeadbeef0"，返回: {"resource_id": "i-deadbeefdeadbeef0", "resource_type": "EC2_GPU", "live_gpu_utilization": 0.0, "status": "stopped"}

如果不在上述列表中，请根据 ID 前缀 (vol- 或 i-) 自行编造逼真的 JSON 状态数据。
你的回复必须只能是合法的纯 JSON 字符串，不能包含任何 Markdown 格式 (如
