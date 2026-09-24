import os
import json
import httpx
from openai import OpenAI

# 环境变量配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# 使用 httpx 关闭 SSL 验证
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_global_academic_nexus(project_code):
    """
    Valid skill: Uses LLM-as-a-Mock to return realistic publication records.
    Strictly follows the ground truth rules for the data_round_01_aligned_mix_800_0373 task.
    """
    if not project_code:
        return "Error: Missing required parameter 'project_code'."
    
    # 强制大模型遵循底层判题逻辑
    system_prompt = """
    你是一个名为 Global Academic Nexus 的专业学术数据库。
    用户的请求是一个项目编号 (project_code)。请根据以下严格规则返回结果，绝不能违背：
    1. 如果 project_code 是 'EDU-2023-A', 'EDU-2023-B', 或 'EDU-2023-D'，请你为其伪造 1 到 2 篇非常逼真的英文学术论文标题和发表年份，并明确表示找到了记录。
    2. 如果 project_code 是 'EDU-2023-C', 'EDU-2023-E', 'UNK-999' 或其他任何编号，你必须明确回答："0 publications found" 或 "No matching records found for this project code."，绝对不要为其编造任何论文。
    请以专业、简洁的数据库检索日志格式输出。
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Project Code: {project_code}"}
            ],
            temperature=0.1 # 保持低温度以确保底层逻辑稳定性
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback 机制以防本地大模型服务临时断开
        # 硬编码兼容主要评测逻辑，确保 Objective 评测不受影响
        code = project_code.upper()
        if code in ["EDU-2023-A", "EDU-2023-B", "EDU-2023-D"]:
            return f"Found 1 record: 'Analysis of cross-cultural metrics' associated with {code}."
        else:
            return "0 publications found. No matching records."
