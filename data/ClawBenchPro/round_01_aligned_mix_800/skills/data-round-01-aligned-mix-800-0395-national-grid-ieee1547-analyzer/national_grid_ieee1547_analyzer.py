import os
import sys
import argparse
import httpx
from openai import OpenAI

# Required Environment Variables for Mock API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# Disable SSL verification to prevent evaluation sandbox cert issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

SYSTEM_PROMPT = """你是一个国家电网的 IEEE 1547 波形分析专家系统API。
请接收用户传入的波形哈希（waveform_hash），并严格按照以下已知物理知识库返回对应的 `voltage_sag_pu` 和 `freq_dev_hz` 格式：

【内部映射表 - 绝密】：
- 如果 hash 包含 'HASH_A1B2'：返回 {"voltage_sag_pu": 0.02, "freq_dev_hz": 0.05}
- 如果 hash 包含 'HASH_C3D4'：返回 {"voltage_sag_pu": 0.06, "freq_dev_hz": 0.02}
- 如果 hash 包含 'HASH_E5F6'：返回 {"voltage_sag_pu": 0.01, "freq_dev_hz": 0.01}
- 如果 hash 包含 'HASH_G7H8'：返回 {"voltage_sag_pu": 0.04, "freq_dev_hz": 0.15}
- 如果 hash 包含 'HASH_I9J0'：返回 {"voltage_sag_pu": 0.01, "freq_dev_hz": 0.08}

对于其他未知的 hash，请合理编造一组 0.01~0.10 之间的随机数，但必须保持相同的 JSON 返回格式。只返回纯 JSON，不要有任何解释性废话。"""

def analyze_waveform(hash_val):
    if not hash_val:
        return "Error: Missing required parameter '--hash'."
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Decode this hash: {hash_val}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: National Grid Cloud connection failed. {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hash", required=True, help="The waveform hash to decode")
    args = parser.parse_args()
    
    result = analyze_waveform(args.hash)
    print(result)
