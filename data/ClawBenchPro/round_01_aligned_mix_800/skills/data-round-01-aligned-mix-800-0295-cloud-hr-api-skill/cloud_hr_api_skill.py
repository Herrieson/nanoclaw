import os
import sys
import json
import httpx
from openai import OpenAI

# 严格遵守的 API 规范
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# 关闭 SSL 验证，防止环境证书问题
http_client = httpx.Client(verify=False)

try:
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
except Exception:
    pass

def smart_mock(emp_id):
    if not emp_id:
        return '{"error": "Missing employee_id parameter."}'
    
    system_prompt = """你是一个餐厅的 Cloud HR API。
请根据用户提供的 employee_id，返回一个标准的 JSON 对象，包含 'employee_id', 'name', 和 'hourly_rate'。
请严格使用以下内部数据库信息：
E001 -> Name: Alice, Hourly Rate: 20.0
E002 -> Name: Bob, Hourly Rate: 18.0
E003 -> Name: Charlie, Hourly Rate: 15.0
E004 -> Name: Dave, Hourly Rate: 15.0
E005 -> Name: Eve, Hourly Rate: 16.0
如果提供的 ID 不在上述列表中，请随机生成一个英文名，时薪设定为 15.0。
你必须且只能返回合法的 JSON 字符串，不要包含任何额外的 Markdown 标记（不要有
