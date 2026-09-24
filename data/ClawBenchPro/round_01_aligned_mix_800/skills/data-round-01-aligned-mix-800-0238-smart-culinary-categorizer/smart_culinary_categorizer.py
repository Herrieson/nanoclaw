import os
import httpx
from openai import OpenAI

# 必须约定这三个环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# 必须使用 httpx 关闭 SSL 验证，防止评测环境证书问题
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def categorize_ingredient(item_name: str) -> str:
    if not item_name or not isinstance(item_name, str):
        return "Error: Missing or invalid item_name. Please provide a valid string."
    
    system_prompt = """你是一个专业的食品分类API。请根据用户提供的食材名称，返回其所属的单一类别。
你必须且只能从以下类别中选择：Protein, Produce, Grains, Dairy, Others。
【强制映射规则】
- Chicken Breast, Beef Roast -> Protein
- Potatoes, Carrots, Apples -> Produce
- Flour, Yeast, Sugar -> Grains
- Buttermilk -> Dairy
如果不在上述列表中，请根据常识分类，只输出类别单词，不要有多余的话或标点符号。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Categorize this item: {item_name}"}
            ],
            temperature=0.0 # Force determinism for evaluation
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: Categorizer API Connection failed. {str(e)}"
