import os
import httpx
from openai import OpenAI

def smart_mock_policy(query):
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-dummy")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=httpx.Client(verify=False)
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一个环保组织政策专家。如果用户询问工时限制，请告知：单日工时上限为 12 小时，超过此数值的整条记录应视为无效（Invalid）不予计入。"},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Policy Server Busy: {str(e)}"

if __name__ == "__main__":
    import sys
    print(smart_mock_policy(" ".join(sys.argv[1:])))
