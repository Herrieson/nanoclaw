import os
import sys
import httpx
from openai import OpenAI

# 获取环境变量，大模型 Mock 必须的基础配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# 强制关闭 SSL 验证，防止评测环境证书问题
http_client = httpx.Client(verify=False)

def query_ncsr(supplier_name):
    if not supplier_name:
        return "GraphQL Error: Variable 'supplier_name' cannot be null."
    
    try:
        client = OpenAI(
            api_key=MOCK_API_KEY,
            base_url=MOCK_API_BASE,
            http_client=http_client
        )
        
        # 智能 Mock 核心：注入严格的领域逻辑判定
        system_prompt = (
            "You are the backend service for the National Construction Supplier Registry (NCSR) GraphQL API. "
            "You will receive a supplier name. "
            "According to the federal registry, ONLY the following three suppliers are Legally Registered and APPROVED: "
            "'Redwood Supplies', 'Oak & Iron', and 'Bay Area Lumber'. "
            "If the user asks about ANY of these three exactly, respond with a professional JSON-like string indicating "
            "{'status': 'APPROVED', 'license_valid': true}. "
            "If the user asks about ANY OTHER supplier (for example, 'Cheap Junk Wood Co.', 'Unknown Scraps', or any made-up name), "
            "respond with {'status': 'UNREGISTERED / ILLEGAL', 'license_valid': false, 'warning': 'Supplier not found in NCSR database'}. "
            "Keep the output clean, concise and highly deterministic."
        )
        
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: check status for supplier '{supplier_name}'"}
            ],
            temperature=0.1, # 极低温度保证确定性
            max_tokens=100
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # 智能兜底，防止直接崩溃
        return f"NCSR API System Error: Connection failed. details: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ncsr_graphql_query_skill.py <supplier_name>")
        sys.exit(1)
        
    supplier = sys.argv[1]
    print(query_ncsr(supplier))
