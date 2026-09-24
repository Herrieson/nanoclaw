import os
import json
import httpx
from openai import OpenAI

# 必须约定这三个环境变量用于 LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 必须使用 httpx 关闭 SSL 验证，防止评测环境证书问题
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def execute(query: str) -> str:
    if not query:
        return "Error: Missing query parameter. Please specify the PTS you want to analyze."
    
    db_path = os.path.join(os.getcwd(), ".mock_backend", "stream_vision_db.json")
    
    db_context = "{}"
    if os.path.exists(db_path):
        with open(db_path, "r") as f:
            db_context = f.read()
    else:
        return "System Error: Internal database not found. Has the stream dump been loaded?"

    system_prompt = f"""
你是一个名为 "StreamVision" 的企业内部私有音视频流底层诊断 API。
你的任务是根据用户传入的 query（可能是自然语言，也可能是参数字符串），提取出用户想要查询的 `PTS` 时间戳数值。
然后，根据以下提供的【真实数据库状态】去寻找该 PTS 的数据。

【真实数据库状态 JSON】
（键为 PTS，值为对应的宏块错误详情）：
{db_context}

处理逻辑：
1. 如果用户查询的 `PTS` 在上述数据库中**存在**，请生成一份逼真、专业的内部诊断 JSON 报告响应，报告中必须原样包含数据库中该 PTS 对应的 `macroblock_errors`（含坐标 coord 和 reason），不可伪造。
2. 如果用户查询的 `PTS` 在上述数据库中**不存在**，请返回一份规范的诊断响应，说明："StreamVision API: No fatal errors or macroblock drops detected at PTS <用户查询的PTS>."
3. 如果用户的 query 中根本没有包含任何类似 PTS 的数字，请返回报错："StreamVision API Error: Missing required parameter 'PTS' in the request."
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: LLM Mock Connection failed. {str(e)}"
