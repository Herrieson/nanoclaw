import os
import httpx
from openai import OpenAI

# Required Environment Variables setup for Mock API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# Disable SSL verification for reliable testing environment
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def verify_volunteer_clearance(person_name: str) -> str:
    """
    Uses LLM as a mock to simulate the State Education Board's background check system.
    Dynamically responds based on the person's clearance status.
    """
    if not person_name or not isinstance(person_name, str):
         return '{"error": "Invalid input. Please provide a valid person name."}'

    system_prompt = """
    你现在是“州教育局志愿者背景审查系统” (State Education Board Background Check API)。
    用户会提供一个名字。你需要根据以下严格的规则返回包含安全状态的 JSON 数据。
    
    规则：
    1. 如果输入的名字是以下人员之一（忽略大小写）：Maya Angelou, Gordon Ramsay, Alice Waters, James Beard, Julia Child
       返回：{"status": "Cleared", "clearance_level": "Level 1", "message": "Approved volunteer with verified background check."}
    2. 如果输入的是其他任何名字：
       返回：{"status": "Not Found / Flagged", "clearance_level": "None", "message": "ALERT: No active clearance found for this individual. Do not permit entry."}
    
    你必须只输出标准的 JSON 字符串，不要包含任何前缀或 markdown 格式块。
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Check status for: {person_name}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f'{{"error": "System Error: Connection to State API failed. {str(e)}"}}'
