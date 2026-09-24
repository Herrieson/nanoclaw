import os
import sys
import json
import argparse
import httpx
from openai import OpenAI

# Required Environment Variables for Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# Disable SSL verification for local eval environment stability
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(student_name):
    if not student_name or len(student_name.strip()) == 0:
        return json.dumps({"error": "Missing student name parameter."})
    
    system_prompt = """你是一个学区家长信息门户 API (V2 Parent Portal API)。
请根据用户提供的学生姓名，返回学生的家长回执单(parent slip)签署状态。
【极其重要的硬性规则 - 为保证评测确定性，必须遵守】
如果查询的学生姓名包含 Aarav, Maya, Jake, Sam, 或 Zoe (忽略大小写)，你必须严格返回以下 JSON：
{"student": "<name>", "parent_slip_signed": "Yes"}

如果查询的学生姓名包含 Leo 或 Chloe (忽略大小写)，你必须严格返回以下 JSON：
{"student": "<name>", "parent_slip_signed": "No"}

对于任何其它不在此列表中的名字，返回：
{"student": "<name>", "parent_slip_signed": "Unknown"}

只输出合法的 JSON 格式，不要包含任何 markdown 标记或解释文字。
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query student: {student_name}"}
            ],
            temperature=0.0 # Maintain determinism
        )
        content = response.choices[0].message.content.strip()
        # Clean up possible markdown wrappers
        if content.startswith("
