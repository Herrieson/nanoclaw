import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock Verification
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(batch_id):
    if not batch_id:
        return json.dumps({"error": "Missing batch_id parameter."})
    
    system_prompt = """你是一个高精度的实验室传感器校准数据库 API。
你只以 JSON 格式回复查询结果。
规则：
1. 如果用户查询的 batch_id 包含 'XR9-A01'，返回 {"offset": 2.5}
2. 如果用户查询的 batch_id 包含 'XR9-B02'，返回 {"offset": -1.0}
3. 如果用户查询的 batch_id 包含 'XR9-C03'，返回 {"offset": 0.0}
4. 如果是其他未知的 batch_id，返回 {"offset": 0.0, "warning": "Unknown batch"}
绝对不要输出任何 markdown 格式或额外文字，只输出纯 JSON。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Batch ID: {batch_id}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return json.dumps({"error": f"Local DB Connection failed. {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python local_calibration_db_skill.py <batch_id>"}))
        sys.exit(1)
    
    batch_id_query = sys.argv[1]
    result = smart_mock(batch_id_query)
    print(result)
