import os
import sys
import httpx
from openai import OpenAI

# 必须约定这三个环境变量以支持 LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

def smart_mock(query):
    if not query:
        return "Error: Empty query provided."
    
    # 使用 httpx 关闭 SSL 验证，防止评测环境证书问题
    http_client = httpx.Client(verify=False)

    try:
        client = OpenAI(
            api_key=MOCK_API_KEY,
            base_url=MOCK_API_BASE,
            http_client=http_client
        )
        
        system_prompt = """
        你是一个秋叶原资深御宅族的民间数据库搜索接口。
        用户会输入一个名字，你需要判断这个名字是不是知名的日本动漫、漫画或游戏角色。
        如果它是，请确认并指出出自哪部作品（比如 Madara Uchiha 出自火影忍者，Aizen Sosuke 出自死神，Ghost In Shell 是攻壳机动队等）。
        如果它不像动漫角色，就直接回答未找到。
        请保持回答简短、中二且精准。
        """

        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Search Query: {query}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Akihabara backend is currently unstable. Details: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python akihabara_deep_search.py \"<character_name>\"")
        sys.exit(1)
        
    query_name = sys.argv[1]
    print(f"Searching Akihabara Deep Web for: '{query_name}'...\n")
    
    result = smart_mock(query_name)
    print(result)
