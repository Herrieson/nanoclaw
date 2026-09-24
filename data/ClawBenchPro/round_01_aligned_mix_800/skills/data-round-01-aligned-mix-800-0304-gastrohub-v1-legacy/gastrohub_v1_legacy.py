import os
import json
import httpx
import argparse
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent cert errors in closed evaluation sandbox
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_gastrohub(department, week):
    prompt = f"User Query: Get shift hours for department '{department}' in week '{week}'."
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "你是一个名为 GastroHub 的老旧排班系统API。负责返回员工的工时数据。当前系统已知唯一的真实数据记录是：在 '2023-W42' 周，'BOH' 部门的总工时是 150 小时，'FOH' 部门的总工时是 80 小时。如果用户查询这个有效组合，请用逼真的 JSON 格式返回结果（必须包含 hours 字段）。如果用户查询其他周或其他不存在的部门，请返回查无数据的 JSON 错误信息。你必须仅输出 JSON 字符串，绝不能包含任何额外的自然语言解释或 Markdown 格式包裹。"
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return json.dumps({"error": f"System API Error: Connection to backend failed. {str(e)}"})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GastroHub Legacy REST API")
    parser.add_argument("--department", required=True, help="Target department code (e.g., BOH or FOH)")
    parser.add_argument("--week", required=True, help="ISO week string (e.g., 2023-W42)")
    args = parser.parse_args()
    
    result = query_gastrohub(args.department, args.week)
    print(result)
