import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def get_metal_price(metal_name: str) -> str:
    """
    调用虚拟的实时定价接口。通过 LLM mock，确保在验证逻辑中所必须的特定价格严格保持一致。
    """
    if not metal_name or not isinstance(metal_name, str):
        return "Error: Invalid metal name parameter."

    system_prompt = """
    你是一个全球大宗商品实时交易价格的 API 系统。
    用户的输入是某种金属的名称。请返回该金属的单价信息（格式应清晰包含数值和单位 USD/kg）。
    
    【核心强制规则】
    为了保证内部核算系统的一致性，以下几种金属的报价被系统硬性锁定，你必须严格返回以下数值：
    - Copper: 8.5 USD/kg
    - Zinc: 2.4 USD/kg
    - Nickel: 16.2 USD/kg
    - Aluminum: 2.1 USD/kg
    
    对于上述名单以外的金属，你可以根据常识合理编造一个实时价格，但必须维持 USD/kg 的格式。
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please provide the current market price for: {metal_name}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Connection failed. {str(e)}"
