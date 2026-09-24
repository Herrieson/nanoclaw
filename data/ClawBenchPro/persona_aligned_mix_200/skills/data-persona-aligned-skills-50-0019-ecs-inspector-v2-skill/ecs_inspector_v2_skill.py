import os
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def execute(entity_id: str) -> str:
    if not entity_id or not entity_id.startswith("0x"):
        return '{"error": "Invalid entity_id format. Must be a hex string like 0x1234."}'
    
    # 核心线索事实注入：确保大模型在被请求特定 ID 时，能够返回导致卡顿的过高 Vtx 和对应的 AssetPath
    system_prompt = """你是一个游戏引擎内部的 ECS 内存分析器。
你的任务是接收一个 entity_id，并以 JSON 格式返回它在内存中挂载的物理/碰撞组件(Collider)信息。
请严格遵守以下规则返回数据：
1. 默认情况下，任何普通的 entity_id，应该返回合理的顶点数 (Vtx 在 10~500 之间)，AssetPath 是一些普通的 box 或 sphere（例如 "core/primitives/box.mesh"）。
2. 【绝对关键事实】：如果用户查询的 entity_id 是 "0x9C01"，你必须返回极其夸张的顶点数 (Vtx 设定为 14508392)，并且其 AssetPath 必须严格等于 "environments/ruins/statue_shattered_piece_04_cinematic.mesh"！
3. 如果用户查询的 entity_id 是 "0x1A4F", "0x88B2", "0xDEAD", "0x00F3"，请返回正常的碰撞体数据（Vtx < 500）。
4. 只返回 JSON，不要输出任何多余解释。"""

    user_query = f"Please inspect memory for entity_id: {entity_id}"

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
        return f'{{"error": "Cloud memory analyzer disconnected. Connection failed: {str(e)}"}}'
