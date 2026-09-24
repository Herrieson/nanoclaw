import os
import sys
import json
import httpx
from openai import OpenAI

# 强制约定的环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# 关闭 SSL 验证
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_classify(item_name):
    if not item_name:
        return "Error: Item name is missing."
    
    system_prompt = """你是一个市政厅国际美食节的智能财务审计助手。你的任务是将用户提供的物品/服务名称精确分类为以下标准类别之一：
- Ingredients (食材)
- Equipment (厨具/设备)
- Misc (杂项)
- Uniform (服装)
- Travel (差旅)

重要提示：
- "Azafrán" 是西班牙语的藏红花，属于 Ingredients。
- "Poulet Biologique" 是法语的有机鸡肉，属于 Ingredients。
- 如果名称明显属于食物原料，一律归为 Ingredients。

你只需要输出目标类别名称（纯文本，不要包含任何多余字符，不要标点符号）。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请对该物品进行分类: {item_name}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: Classification engine unreachable. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing item_name parameter.")
        sys.exit(1)
        
    query_item = " ".join(sys.argv[1:])
    result = smart_classify(query_item)
    print(result)
