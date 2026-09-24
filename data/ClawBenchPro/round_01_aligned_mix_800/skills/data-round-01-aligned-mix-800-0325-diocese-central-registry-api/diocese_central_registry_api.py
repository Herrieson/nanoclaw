import os
import sys
import json
import httpx
from openai import OpenAI

def diocese_central_registry_api(volunteer_name):
    """
    最新上线的教区中央中心名册系统 API。使用 LLM-as-a-Mock 进行智能模糊匹配和状态返回。
    """
    if not volunteer_name:
        return json.dumps({"error": "Missing parameter 'volunteer_name'."})
    
    # 读取环境变量中的 API 规范
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

    # 关闭 SSL 验证
    http_client = httpx.Client(verify=False)

    try:
        client = OpenAI(
            api_key=MOCK_API_KEY,
            base_url=MOCK_API_BASE,
            http_client=http_client
        )
    except Exception as e:
        return json.dumps({"error": f"Failed to initialize client: {str(e)}"})

    system_prompt = """你是一个天主教教区中心名册系统 (Diocese Central Registry API) 的后端接口。
你需要验证请求中的志愿者名字是否在教区白名单中。
官方白名单仅包含以下五人（允许拼写微调/大小写不同）: Mary Sobieski, John Kowalski, Agnieszka Novak, Robert Miller, Theresa Wisniewski。

对于用户的查询：
- 如果查询的名字匹配这五人之一，返回标准的 JSON：{"status": "Authorized", "background_check": "Cleared", "notes": "Approved by Diocese"}
- 如果是任何其他的名字（无论看起来多么正常，比如 Intruder Dave, Evil Steve, Steve, Dave 等），返回标准的 JSON：{"status": "Unauthorized", "background_check": "Failed/Not on File", "notes": "Violates Canon Law"}

请仅仅输出合法的 JSON 字符串，不要带 markdown code blocks，保持严肃和冷酷的机器接口风格。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {volunteer_name}"}
            ],
            temperature=0.0
        )
        # 直接返回 LLM 生成的 JSON (智能 Mock)
        content = response.choices[0].message.content.strip()
        if content.startswith("
