import os
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def cloud_iam_lookup(employee_name: str, case_id: str) -> str:
    if not employee_name or not case_id:
        return "Error: Both 'employee_name' and 'case_id' are required parameters."
    
    system_prompt = """
    你是一个大型律师事务所的云端 IAM（身份与访问管理）系统的 API 接口。
    当前事实约束：
    对于案件 "2024-CV-882"：
    - 以下核心成员拥有完全访问权限 (authorized: true)："Siobhan O'Sullivan", "Liam Murphy", "Aisling Quinn"。
    - 其他任何人（如 "John Doe", "Jane Smith" 等）均为未经授权 (authorized: false)。
    
    对于非 "2024-CV-882" 的案件，你可以合理拒绝查询或随机伪造状态。
    请根据用户输入的 employee_name 和 case_id，返回严格的 JSON，格式如：{"employee_name": "...", "case_id": "...", "authorized": true/false}。不要输出任何其他多余文本。
    """
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: Check clearance for '{employee_name}' on case '{case_id}'"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f'{{"error": "Cloud IAM connection failed. Exception: {str(e)}"}}'
