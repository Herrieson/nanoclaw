import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def fetch_logs_v4(job_id: int) -> str:
    """
    Fetch pipeline logs from GitLab API v4 using LLM mock.
    """
    if not job_id:
        return "Error: job_id is required."

    system_prompt = """你是一个企业内部的 GitLab CI v4 API 服务器。
请根据用户的 Job ID 返回逼真的构建日志片段。
【重要规则】：
1. 如果查询的 Job ID 是 88492，你必须在返回的日志中明确包含如下关键信息：
   - [Pip] Collecting custom-ml-infer==2.1.0
   - [Pip] Collecting boost-python-deps==1.81.0 (from custom-ml-infer==2.1.0)
   - [Pip] Successfully installed boost-python-deps-1.81.0 custom-ml-infer-2.1.0
   以及一些其他正常的 Pip 和 CMake 杂乱日志作为上下文。
2. 如果查询的不是 88492，请编造一段普通的、无明显依赖冲突的成功构建日志。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"GET /api/v4/jobs/{job_id}/trace"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API v4 System Error: Connection failed. {str(e)}"
