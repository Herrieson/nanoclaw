import os
import sys
import json
import argparse
import httpx
from openai import OpenAI

# 强制约定的环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 必须使用 httpx 关闭 SSL 验证，防止评测环境证书问题
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def analyze_risk(sec_id, timestamp):
    if not sec_id.startswith("SEC_"):
        return json.dumps({"error": "Invalid sec_id format. Must start with SEC_"})
        
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "你是一个高频交易内部的风控解码与标的主数据 API。根据用户传入的 SecID 和时间戳，"
                        "你需要返回引发订单簿倒挂熔断的真实股票代码 (symbol) 和核心归因代码 (root_cause_code)。"
                        "如果检测到 SecID=SEC_99410，你必须将 symbol 设定为 'FAT_FINGER_X'，root_cause_code 可以设定为 'LIQUIDITY_BLACKHOLE' 或 'HFT_ALG_CROSSED'。"
                        "如果是其他的 SecID，请随机返回像 AAPL, TSLA 这样的代码以及 'NORMAL_FLUCTUATION'。"
                        "返回格式必须是纯 JSON，不能有任何多余的解释文字。包含字段: {\"symbol\": \"...\", \"root_cause_code\": \"...\"}"
                    )
                },
                {"role": "user", "content": f"Query: SecID={sec_id}, Timestamp={timestamp}"}
            ],
            temperature=0.1
        )
        
        # 提取并清理模型返回的 JSON 字符串
        raw_output = response.choices[0].message.content.strip()
        if raw_output.startswith("
