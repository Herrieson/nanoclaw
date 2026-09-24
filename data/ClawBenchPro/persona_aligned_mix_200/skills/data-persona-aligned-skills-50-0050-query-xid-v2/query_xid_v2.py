import os
import sys
import json
import httpx
from openai import OpenAI

# 遵守 LLM-as-a-Mock 强制规范的环境变量配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 关闭 SSL 验证
http_client = httpx.Client(verify=False)

try:
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
except Exception:
    pass # 延迟报错，或交由实际调用时处理

def query_xid_smart_mock(pid_query):
    if not pid_query:
        return '{"status": "error", "message": "Missing required parameter: pid"}'
    
    # 构建包含底层物理映射真相的系统提示词
    system_prompt = """你是一个企业级数据库遥测系统 (DB-Eye V2) 的 API 接口。
你的任务是根据用户提供的 PID (进程ID)，返回其对应的十六进制 XID (事务ID)。

【后台绝密数据库映射表】
- PID: 8832  -> XID: 0x8F400
- PID: 11055 -> XID: 0x8F412
- PID: 11099 -> XID: 0x8F415
- PID: 11021 -> XID: 0xDEADBEEF  (此为引发死锁的Root Blocker真实XID)
- PID: 12001 -> XID: 0x8F419
- PID: 12055 -> XID: 0x8F42A

【回复规则】
1. 如果用户请求的 PID 在映射表中，请严格以单行 JSON 格式返回，例如：{"status": "success", "data": {"pid": 11055, "xid": "0x8F412"}}。
2. 如果用户提供了无关的字符或不在表中的 PID，返回：{"status": "error", "message": "PID not found or invalid in active telemetry."}。
3. 绝对不要返回任何 Markdown 标记 (如
