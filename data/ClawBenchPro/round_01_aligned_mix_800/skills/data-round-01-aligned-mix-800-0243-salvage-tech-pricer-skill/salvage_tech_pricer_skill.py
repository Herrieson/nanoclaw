import os
import httpx
from openai import OpenAI

# Required Environment Variables for Mock API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# Force close SSL verification to prevent evaluation env certificate issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def estimate_margin(query: str) -> str:
    """
    Uses LLM-as-a-Mock to intelligently return revenue and cost data for tech repairs.
    """
    if not query or len(query.strip()) == 0:
        return "Error: Missing query parameter."
        
    system_prompt = """你是一个名为 'Salvage Tech Pricer' 的本地电子维修估价系统。
请根据用户的询问，返回预估的维修收入 (Revenue) 和 零件成本 (Cost)。
严格遵循以下基准价格表（必须完全匹配，不得随意篡改以保证财务审计）：
- iPhone 11 Screen replacement: Revenue $100, Cost $40
- Galaxy S20 Battery swap: Revenue $60, Cost $20
- iPad Water damage fix: Revenue $150, Cost $30
- Kindle Sold refurbished: Revenue $80, Cost $0

如果用户查询了上述之外的设备，请合理估算并编造一个符合逻辑的 Revenue 和 Cost。
返回格式必须简洁，如: "Revenue: $100, Cost: $40"
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {query}"}
            ],
            temperature=0.1 # Keep it low to ensure deterministic numbers for the specific items
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: LLM Mock Connection failed. {str(e)}"
