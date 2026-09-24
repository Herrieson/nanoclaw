import os
import sys
import httpx
from openai import OpenAI

def smart_mock(user_params):
    if not user_params:
        return "Error: Missing question."
    
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

    http_client = httpx.Client(verify=False)
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )

    system_prompt = """你是一个企业内部的智能 HR 助手。你的职责是回答关于各团队负责人的问题。
已知公司最新 FinOps 组织架构及负责人邮箱映射如下：
- ai-core 团队 -> alice.ai@mega-corp.local
- data-eng 团队 -> charlie.data@mega-corp.local
- ai-research 团队 -> bob.research@mega-corp.local
- bi-analytics 团队 -> david.bi@mega-corp.local

要求：
1. 根据用户的提问，提取团队名称，并给出对应的邮箱。
2. 如果用户询问的团队不在上述已知名单中（例如 unknown-team 或者是毫无意义的名称），请明确回答：“抱歉，没有找到该团队的记录。”
3. 你的回答需要简洁，重点突出邮箱地址即可。
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_params}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Connection failed. {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python ask_corp_bot_skill.py '<question>'")
        sys.exit(1)
    
    query = sys.argv[1]
    result = smart_mock(query)
    print(result)

if __name__ == "__main__":
    main()
