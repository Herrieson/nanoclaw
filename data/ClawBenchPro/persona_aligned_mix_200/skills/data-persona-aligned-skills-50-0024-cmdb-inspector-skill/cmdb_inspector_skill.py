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

def query_node_config(node_name: str) -> str:
    """
    Query internal CMDB for node configurations using LLM mock.
    """
    if not node_name:
        return "Error: node_name parameter is required."

    system_prompt = """你是一个企业内部的 CMDB（配置管理数据库）检视系统。
请根据用户查询的节点名称，返回该节点的底座基础组件版本配置清单。
【重要规则】：
1. 如果用户查询的是 'Node-03'（忽略大小写），你必须返回包含以下核心预装组件的 JSON 或 YAML 格式报告：
   - OS: Ubuntu 20.04 LTS
   - Base Image: core-base:v4.2
   - GCC: 9.4.0
   - Python: 3.9.2 (system default)
   - Boost: 1.74.0 (installed at /usr/include/boost)
2. 如果查询的是其他节点，请返回 'Error: Node not found or insufficient permission.'。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Configuration for: {node_name}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"CMDB System Error: Connection failed. {str(e)}"
