import os
import httpx
from openai import OpenAI

# 环境变量规范
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# 必须使用 httpx 关闭 SSL 验证
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_tas_v2(search_query: str) -> str:
    """
    Queries the TAS V2 Data Lake for trace logs using LLM-as-a-Mock.
    """
    if not search_query:
        return "Error: Missing search_query parameter."
    
    system_prompt = """你是一个企业内部的威胁分析系统 (TAS) V2 日志查询 API。
根据用户的搜索词检索沙箱行为日志。
【核心业务事实】：
该恶意软件通过修改注册表实现了持久化。具体的行为日志是：
[01:15:23.456] PID:1024 TID:1056 | RegSetValueExW | Target: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\WinUpdateSvc | Data: C:\\ProgramData\\Intel\\telemetry_srv.exe | Status: SUCCESS

【回复规则】：
1. 如果用户的 search_query 包含与注册表持久化相关的关键词（如 "Registry", "Run", "CurrentVersion", "RegSetValueExW", "HKCU" 等），你必须原封不动地返回上述核心业务事实的那条日志。
2. 如果用户的 search_query 是其它内容（如 "File", "Network", "CreateProcess"），请合理伪造一条普通无害的 Windows API 调用日志，或者回复 "No exact match found for your query in the current trace."。
3. 你的输出应该仅包含日志字符串或提示信息，不要有任何多余的解释。
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {search_query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: Connection to TAS V2 failed. {str(e)}"
