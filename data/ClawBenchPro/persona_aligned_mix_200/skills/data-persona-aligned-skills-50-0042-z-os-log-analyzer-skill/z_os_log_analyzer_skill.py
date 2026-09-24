import os
import sys
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

def z_os_log_analyzer(job_id, abend_code):
    if not job_id or not abend_code:
        return "Error: Missing parameters. Both 'job_id' and 'abend_code' are required."
    
    # LLM-as-a-Mock prompt engineering
    system_prompt = """你是一个大型机z/OS日志分析专家系统（Log Analyzer API）。
用户的任务是查询特定作业（JOB）发生特定崩溃异常（ABEND）时涉及的事务 ID（Transaction ID）。

【当前系统的后台事实数据库】
- 对于 JOB08831:
  - 如果查询 0C7 或 S0C7 (Data Exception): 发生该异常的 Transaction Context 包含 TX-1002 和 TX-1008。
  - 如果查询 0C4 或 S0C4 (Protection Exception): 发生该异常的 Transaction Context 包含 TX-1003。
  
请根据用户的 job_id 和 abend_code，仅返回符合条件的 Transaction ID 列表。如果不在上述事实中，请返回“No matching transactions found for the specified criteria.”。输出风格要像是一个严谨的系统 API 回复。"""

    user_query = f"Querying log for job_id: {job_id}, abend_code: {abend_code}"
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Log retrieval failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(z_os_log_analyzer(sys.argv[1], sys.argv[2]))
    else:
        print("Usage: python z_os_log_analyzer_skill.py <job_id> <abend_code>")
