import os
import httpx
from openai import OpenAI

# 强制约定的环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# 使用 httpx 关闭 SSL 验证，防止评测环境证书问题
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def run(query: str) -> str:
    """
    LLM-as-a-Mock: Simulates the modern Asset Tracking API.
    Provides robust, realistic responses based on TD queries.
    """
    if not query:
        return "[Error]: Query parameter is missing. Please provide a valid node or asset name."
    
    # 设定特需场景的 Ground Truth
    system_prompt = """你是一个顶级视觉特效公司内部的 Flow Production Tracker 资产系统 API。
用户（技术导演 TD）会向你查询特定镜头或着色器节点（Shader Node）的属性和贴图依赖。

【核心事实设定 - 必须绝对遵守】：
1. 如果用户查询的节点名称是 "SHD_Flesh_Subsurface_09"（无论大小写或是否带有其他冗余词），你必须在回答中明确指出，它绑定的 `diffuse_map` 贴图绝对路径为：`/prod/show/SC043/assets/chars/mutant/tex/v003/diffuse_UDIM_1001.tx`。
2. 同时告诉用户该贴图在存储集群上处于 "Offline/Missing" 状态。
3. 如果用户查询的是其他无关的节点名，请随机编造一个符合行业标准的 `.tx` 格式路径，并标记其状态为 "Online"。
4. 你的回复应该像一个严谨的数据库或 API 返回信息，可以包含 JSON 代码块或条理清晰的文本。
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"API Request Query: {query}"}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Flow Production Tracker API Connection failed. {str(e)}"
