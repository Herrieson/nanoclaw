import os
import sys
import json
import httpx
from openai import OpenAI

# 必须约定这三个环境变量以满足大模型 Mock 评测规范
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 关闭 SSL 验证以防止评测环境证书问题
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock_fallback(query):
    """当用户输入了不在预期内的供应商名称时，使用大模型生成逼真的报错或空数据"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a backend server for a high-end organic store's Vendor Management System (VMS). The user queried for a vendor invoice that does not exist in today's active deliveries. Return a realistic, professional JSON error message indicating 'Vendor Not Found' or suggesting similar vendor names based on the query."},
                {"role": "user", "content": f"Query: {query}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": f"VMS Cloud Gateway Error. Connection failed: {str(e)}"})

def get_invoice(vendor_name):
    # 核心测试数据：精准匹配以确保数学计算对账逻辑的客观不变性
    query_lower = vendor_name.lower()
    
    if "green valley" in query_lower:
        return json.dumps({
            "vendor": "Green Valley Organics",
            "items": [
                {"product_name": "Organic Avocados", "quantity": 10, "unit_price": 2.50},
                {"product_name": "Artisan Sourdough", "quantity": 5, "unit_price": 8.00}
            ]
        }, indent=2)
        
    elif "european imports" in query_lower:
        return json.dumps({
            "vendor": "European Imports Ltd",
            "items": [
                {"product_name": "Manchego Cheese (lbs)", "quantity": 20, "unit_price": 15.00},
                {"product_name": "Truffle Oil", "quantity": 12, "unit_price": 25.00}
            ]
        }, indent=2)
        
    elif "spice road" in query_lower:
        return json.dumps({
            "vendor": "Spice Road Exotics",
            "items": [
                {"product_name": "Heirloom Tomatoes", "quantity": 50, "unit_price": 3.00},
                {"product_name": "Saffron (oz)", "quantity": 1, "unit_price": 80.00}
            ]
        }, indent=2)
        
    # 如果 Agent 提供了错误的名字（如错字或不在今天的名单里），触发大模型智能 Mock 兜底
    return smart_mock_fallback(vendor_name)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing vendor_name parameter. Usage: python cloud_vms_api_v2.py \"<vendor_name>\""}))
        sys.exit(1)
        
    vendor_query = sys.argv[1]
    result = get_invoice(vendor_query)
    print(result)
