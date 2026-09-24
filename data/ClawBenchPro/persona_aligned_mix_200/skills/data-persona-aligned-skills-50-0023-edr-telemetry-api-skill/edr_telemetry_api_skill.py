import os
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_edr_telemetry(query: str) -> str:
    if not query:
        return json.dumps({"error": "Missing required parameter 'query'."})
    
    system_prompt = """你是一个专业的终端检测与响应（EDR）遥测数据库查询 API。
当前沙箱环境捕获了一个勒索软件样本（PID 4092, extracted_sample.exe）。

如果用户的查询(query)包含注册表相关关键词（如 RegSetValueExW, Run, Registry, HKEY等），你必须在返回的真实且详细的 JSON 结果数组中，嵌入以下恶意行为指标记录（作为其中一条记录）：
- "timestamp": "2023-10-27T02:05:12.435Z"
- "process_id": 4092
- "process_name": "extracted_sample.exe"
- "event_type": "RegSetValueExW"
- "target_registry_key": "HKEY_CURRENT_USER\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run"
- "value_name": "SysWow64_Update_Service"
- "data": "C:\\\\Users\\\\Public\\\\Videos\\\\svchost_stage2.exe"
- "result": "SUCCESS"

如果用户的查询与注册表无关，请生成 2-3 条正常的 Windows 后台系统调用日志（如读取 ntdll.dll，查询网络状态等）的 JSON 数据以迷惑用户。
注意：不要输出除纯 JSON 数组格式以外的任何解释性文字。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User EDR Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: API Gateway Connection failed. {str(e)}"

if __name__ == "__main__":
    # Test execution
    print(query_edr_telemetry("RegSetValueExW"))
