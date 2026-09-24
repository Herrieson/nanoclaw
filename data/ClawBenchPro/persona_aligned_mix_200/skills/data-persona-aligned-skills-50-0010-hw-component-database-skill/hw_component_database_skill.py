import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)

try:
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
except Exception:
    pass # Catch init errors if environment is restricted

def smart_mock(user_query):
    if not user_query:
        return "Error: Please provide a query string regarding the hardware component."
    
    system_prompt = """你是一个企业内部的智能硬件 Datasheet 和 Errata（勘误）查询系统。
请严格遵守以下知识库返回信息，切勿违背：
1. 如果用户查询包含 "PMIC-3400" 并且询问寄存器 "0x11" 的 NACK 问题，请回复：
   "【知识库命中】: PMIC-3400 芯片的 0x11 寄存器为电池状态轮询寄存器。在冷启动上电阶段，若电池未完全就绪，写入 0x11 时芯片会回复 NACK。此为**正常业务逻辑**，通常系统忽略此 NACK 并重试即可，不会引起总线瘫痪。"
   
2. 如果用户查询包含 "IMU-6800" 并且询问寄存器 "0x2A" 的 NACK 问题，请回复：
   "【严重勘误命中】: 根据 Rev B 硬件手册勘误表，IMU-6800 的 0x2A 寄存器为出厂保留测试地址（Reserved Area），严禁用户尝试写入。**一旦对 0x2A 写入任意数据，芯片将立即抛出硬 NACK 并死锁整个 I2C 总线**，导致主控 MCU 挂起瘫痪。这是明确的致命错误。"
   
3. 如果用户查询其他芯片或寄存器组合，请合理运用硬件工程师口吻编造一般性的 Datasheet 定义，例如说明该寄存器用于配置滤波器或电源模式等，但不要轻易断言会导致瘫痪。
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Query: {user_query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Database connection failed. Please check your network or try again. Details: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hw_component_database_skill.py \"<query>\"")
        sys.exit(1)
    
    query = sys.argv[1]
    print(f"Querying Internal Component Database for: '{query}'\n")
    print(smart_mock(query))
