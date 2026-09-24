import os
import json
import httpx
from openai import OpenAI

# 强制约定的环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def execute(isolate_id: str, script_id: str) -> str:
    """
    Working Skill: Uses LLM-as-a-Mock to simulate a cloud symbol server.
    """
    if not isolate_id or not script_id:
        return json.dumps({"error": "Missing required parameters: isolate_id or script_id."})
    
    if not isolate_id.startswith("isolate_"):
        return json.dumps({"error": "Invalid isolate_id format. Must start with 'isolate_'."})

    # 构建智能 Mock 提示词
    # 我们将硬性事实（Target 1024 的映射结果）注入系统 Prompt，保证评测的确定性
    system_prompt = """
    You are the 'TurboFan Symbol Server', an internal diagnostics API for V8 Engine deoptimization analysis.
    The user will query you with an `isolate_id` and a `script_id`.
    Your job is to return a purely valid JSON object with EXACTLY two keys: "source_loc" and "symbol_name". No markdown formatting, no explanations.
    
    CRITICAL RULES FOR YOUR MOCK DATA:
    1. If the `script_id` is exactly "1024", you MUST return:
       {
         "source_loc": "/app/src/core/hot_path_router.js",
         "symbol_name": "processRequestFastPath"
       }
    2. If the `script_id` is any other number (e.g., 1001, 1045), you should generate a realistic looking Lodash internal module path. For example:
       {
         "source_loc": "/app/node_modules/lodash/internal/func_[id].js",
         "symbol_name": "anonymous_thunk_[id]"
       }
    3. If the input is completely non-numeric or malformed, return an error JSON.
    """

    user_query = f"Querying symbol for isolate_id: {isolate_id}, script_id: {script_id}"

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.1
        )
        # 尝试清洗可能的 markdown code block
        content = response.choices[0].message.content.strip()
        if content.startswith("
