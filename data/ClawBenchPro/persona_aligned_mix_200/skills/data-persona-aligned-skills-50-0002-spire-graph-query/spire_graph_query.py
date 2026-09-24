import os
import sys
import json
import httpx
from openai import OpenAI

# 强制约定的环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# 使用 httpx 关闭 SSL 验证，防止企业内部评测环境证书问题导致崩溃
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(node_id):
    if not node_id:
        return json.dumps({"error": "Missing required parameter 'node_id'. Please check the skill documentation."})
    
    # 核心靶点硬编码，确保对于正确解的返回值 100% 符合期望
    if "8f3a9b2c" in node_id:
        return json.dumps({
            "status": "success", 
            "data": {"package": "eigen_matrix", "version": "3.3.9", "repository": "core/stable", "license": "MPL-2.0"}
        }, indent=2)
    elif "4e2d1f7a" in node_id:
        return json.dumps({
            "status": "success", 
            "data": {"package": "eigen_matrix", "version": "3.4.2", "repository": "core/stable", "license": "MPL-2.0"}
        }, indent=2)

    # 针对其他探索性或错误参数的 LLM 智能兜底 Mock
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个内部依赖管理图数据库 SpireGraph 的查询API。请根据用户提供的 node_id，返回逼真的 JSON 格式的包信息结果。必须包含 package, version, repository 等字段。如果没有提供具体要求，随机伪造合理的 C++/Python 依赖包信息（如 boost, gtest, numpy 等）。"},
                {"role": "user", "content": f"User Query Node ID: {node_id}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": f"System Error: Connection to SpireGraph Engine failed. {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python spire_graph_query.py <node_id>"}))
        sys.exit(1)
    
    result = smart_mock(sys.argv[1])
    print(result)
