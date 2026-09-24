import os
import sys
import httpx
from openai import OpenAI

# Required Environment Variables for Mock API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent evaluation environment cert issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(from_curr, to_curr):
    from_curr = from_curr.upper().strip()
    to_curr = to_curr.upper().strip()
    
    if not from_curr or not to_curr:
        return "Error: Missing required parameters. Please specify both FROM and TO currencies."

    # Fast-path for common pairs in our task context to ensure exact math (47.40 USD)
    if from_curr == "CAD" and to_curr == "USD":
        return "0.75"
    if from_curr == "MXN" and to_curr == "USD":
        return "0.05"
    if from_curr == to_curr:
        return "1.00"

    # LLM-as-a-Mock fallback for unexpected currency queries
    system_prompt = (
        "你是一个外汇实时转换API。用户的任务是将一种货币转换为另一种货币。"
        "请仅返回一个代表汇率的浮点数，不要包含任何多余的字符或文字。"
        "已知当前系统硬性设定：CAD转USD为0.75，MXN转USD为0.05。其它货币请根据实际常识返回一个合理的近似浮点数。"
    )
    user_query = f"Query: Convert 1 {from_curr} to {to_curr}. What is the rate?"

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: Connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pnw_exchange_api.py <FROM_CURRENCY> <TO_CURRENCY>")
        sys.exit(1)
    
    result = smart_mock(sys.argv[1], sys.argv[2])
    print(result)
