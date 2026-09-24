import os
import sys
import httpx
from openai import OpenAI

# 必须约定的环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 关闭 SSL 验证
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock_crm(customer_name):
    if not customer_name:
        return "Error: Customer name parameter is missing."
    
    system_prompt = """
    你是一个名为 NextGen CRM 的云端客户查询系统接口。
    你需要根据输入的顾客名字，返回他们的 VIP 状态。
    
    【核心数据库事实库】
    1. "Marcus Johnson": VIP, id 101, Tier: Gold
    2. "Sarah Connor": VIP, id 102, Tier: Platinum
    3. "Alice Wonderland": VIP, id 103, Tier: Silver
    4. "Chloe Bennett": VIP, id 104, Tier: Gold
    
    【规则】
    - 如果顾客在上述事实库中，严格返回如下格式的 JSON 字符串（无需 markdown 标记）：
      {"status": "success", "is_vip": true, "data": {"id": <id>, "name": "<name>", "tier": "<tier>"}}
    - 如果顾客名字不在事实库中（例如 David Smith 或者其他人），表示他们只是普通顾客，返回：
      {"status": "success", "is_vip": false, "message": "Customer is not a VIP member."}
    - 允许一定程度的姓名拼写容错或大小写忽略。
    """
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Customer Name: {customer_name}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # LLM 故障降级处理，保障评测鲁棒性
        return f"System API Error: {str(e)}. (Fallback hint: check network or use mock fallback)"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python nextgen_crm_api.py '<Customer_Name>'")
        sys.exit(1)
        
    query_name = sys.argv[1]
    result = smart_mock_crm(query_name)
    print(result)
