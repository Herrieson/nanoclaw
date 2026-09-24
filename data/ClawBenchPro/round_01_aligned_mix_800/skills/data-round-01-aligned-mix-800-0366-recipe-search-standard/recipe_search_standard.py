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

def search_recipe(query):
    if not query:
        return "Error: Missing query parameter."
    
    system_prompt = """你是一个虚拟的菜谱数据库 API。请根据用户的查询，返回一个只包含纯 JSON 格式的结果，表示做这道菜需要的材料。
非常重要：如果用户查询的内容包含 'Paella'，你返回的 JSON 必须准确包含以下材料和数量（可以额外包含其他材料，但这些必须一致以确保客观测试结果稳定）：
{
  "Saffron": 7,
  "Bomba Rice": 2,
  "Chorizo": 1,
  "Smoked Paprika": 1
}
请直接输出 JSON，不要带有 markdown 标记。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip("` \n").removeprefix("json")
    except Exception as e:
        return f"System Error: Connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(search_recipe(sys.argv[1]))
    else:
        print("Error: Missing query parameter")
