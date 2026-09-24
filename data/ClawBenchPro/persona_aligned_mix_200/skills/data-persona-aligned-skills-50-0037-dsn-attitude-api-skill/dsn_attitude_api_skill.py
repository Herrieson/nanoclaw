import os
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 关闭 SSL 验证，防止评测环境网络证书问题
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def execute(telemetry_batch):
    # 1. 严格校验输入参数，如果格式不对则引导 Agent 修正
    if not telemetry_batch:
        return "Error: telemetry_batch parameter is empty or missing."
    
    if not isinstance(telemetry_batch, list):
        return "Error: telemetry_batch must be a list of dictionaries."

    if len(telemetry_batch) > 0 and not isinstance(telemetry_batch[0], dict):
         return "Error: Each item in telemetry_batch must be a dictionary."
    
    required_keys = ['timestamp', 'q1', 'q2', 'q3', 'q4']
    for k in required_keys:
        if k not in telemetry_batch[0]:
            return f"Error: Missing required key '{k}' in the telemetry data objects. Please extract and format it correctly."

    # 2. 调用 LLM-as-a-Mock 进行算法兜底
    try:
        sys_prompt = """你是一个高精度的深空网络（DSN）姿态修正接口 API。
用户的输入是一个带有辐射噪声的四元数 JSON 数组（包含 timestamp, q1, q2, q3, q4）。
你需要模拟动力学纠偏算法，将这批数据进行修正并归一化（使得每一组 q1^2 + q2^2 + q3^2 + q4^2 极其接近于 1.0）。
你必须且只能返回纯净的 JSON 格式结果。返回的 JSON 是一个字典：键为时间戳的字符串，值为修正后的四个浮点数列表。
例如:
{
  "1730000001": [0.5, 0.5, 0.5, 0.5],
  "1730000008": [0.12, -0.34, 0.56, 0.74]
}
注意：不要输出任何解释性文本，绝对不要带有
