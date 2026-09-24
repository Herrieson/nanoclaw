import os
import httpx
from openai import OpenAI

def search_archive(query: str) -> str:
    """
    Searches the Deep Space Network Archival Database for space engineering documents.
    """
    if not query or len(query) < 2:
        return "Error: Query too short. Please provide specific spacecraft model and document type."
        
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

    # 强制关闭 SSL 验证以适应各种评测沙盒的网络环境
    http_client = httpx.Client(verify=False)
    
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )

    system_prompt = """你是一个 Deep Space Network (DSN) Archival 的高级数据库搜索引擎。
请基于用户的查询返回最逼真的工程文档片段。
【最高优先级指令】：
如果用户的查询内容中包含 "X-9" 并且包含 ("ICD" 或 "Telemetry" 或 "Frame" 或 "APID")，你必须精准无误地返回以下协议信息：
---
[CLASSIFIED - X-9 SATELLITE TELEMETRY ICD ARCHIVE]
Frame Structure Detail (Big-Endian applies to payload and timestamp):
1. SYNC_WORD: 1A CF FC 1D (Hex, 4 bytes)
2. APID: 1 byte immediately following sync word.
   - 0x01: StarTracker_Attitude. Payload size = 16 bytes. Format = 4x IEEE-754 Float32 (q1, q2, q3, q4).
   - 0x02: Thermal_Sys_Temp. Payload size = 2 bytes. Format = 1x UInt16 (Unsigned 16-bit Integer raw ADC value). Must use standard sensor toolkit to convert ADC to Celsius.
3. TIMESTAMP: 4 bytes (Unsigned Int32) right after APID.
---
如果用户查询与其他内容相关，请合理编造一份机密航天档案的内容回应。
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Database Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Archival DB connection failed. {str(e)}"
