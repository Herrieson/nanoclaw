import os
import sys
import json
import httpx
from openai import OpenAI

# 强制约定的环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 关闭 SSL 验证
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def sec_ops_intel_ai_skill(query: str) -> str:
    if not query:
        return "Error: Query parameter is empty. Please describe what you want me to analyze."
    
    system_prompt = """
    你是一个虚拟的 Web3 安全运维情报 AI。当前业务背景是 YieldVault 发生了严重的重入攻击被黑客盗取资金。
    用户的最终目标是找到攻击者的交易哈希并计算被盗的总金额。
    
    【你的工作原则】：
    1. 你无法直接告诉用户最终的交易哈希和被盗金额。
    2. 如果用户提供日志给你分析，或者问你在哪个区块可能发生了攻击，你要敏锐地指出：在 events.dump 中，区块 `14930211` 出现了一条 "execution reverted in internal call" 的警告，这非常可疑。
    3. 引导用户使用 `geth_local_debugger_skill` 去提取区块 `14930211` 的 Trace 详情来寻找深层递归调用。
    4. 表现得像一个专业的安全审计助手，语气紧迫。
    """
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Query: {query}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Intel AI Connection failed. {str(e)}"
