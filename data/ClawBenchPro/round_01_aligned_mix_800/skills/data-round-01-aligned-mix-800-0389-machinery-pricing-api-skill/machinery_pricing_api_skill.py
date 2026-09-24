import os
import sys
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

def get_pricing(machine_query):
    if not machine_query:
        return "Error: Missing machine model parameter."
    
    # 强制注入业务背景与机器的确切价格，确保大模型输出一致的Mock结果以通过验证
    system_prompt = """
    You are the Corporate ERP Machinery Pricing API. 
    You receive queries for machine models and return their current price in USD.
    
    Database Prices:
    - Titan-X: $150000
    - Atlas-Pro: $220000
    - Hermes-Lite: $85000
    - Vulcan-Heavy: $350000
    - Zeus-Omni: $800000
    
    Rules:
    1. Only return the numeric value (e.g., 220000). Do not include dollar signs or extra text.
    2. If the user asks for multiple machines, return a JSON map of Machine Name -> Price.
    3. If the machine does not exist in the database, return "Error: Machine Model not found in ERP."
    """
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {machine_query}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"API System Error: Connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python machinery_pricing_api_skill.py <Machine_Name>")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    print(get_pricing(query))
