import os
import sys
import json
import subprocess

# Auto-install dependencies if missing to ensure bulletproof execution
try:
    import httpx
    from openai import OpenAI
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "openai", "httpx"], check=True)
    import httpx
    from openai import OpenAI

def nova_telemetry_query_skill(traj_id: str) -> str:
    """
    Queries the Nova Telemetry mock database via LLM to fetch RLHF trajectory details.
    """
    if not traj_id:
        return "Error: Missing required parameter 'traj_id'."

    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

    # Disable SSL verification for stable eval environment execution
    http_client = httpx.Client(verify=False)

    try:
        client = OpenAI(
            api_key=MOCK_API_KEY,
            base_url=MOCK_API_BASE,
            http_client=http_client
        )
    except Exception as e:
        return f"System Error: Failed to initialize OpenAI client. {str(e)}"

    system_prompt = """你是一个高逼真的大厂内部 RLHF 轨迹遥测数据库 (Nova Telemetry)。
用户会提供一个 `traj_id`。你必须返回该轨迹的详细 JSON 数据。
【严格约束】：你返回的内容必须是纯合法的 JSON 字符串，绝不能包含 markdown 代码块（如
