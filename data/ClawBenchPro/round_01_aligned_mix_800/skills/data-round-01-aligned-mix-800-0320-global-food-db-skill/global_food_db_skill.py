#!/usr/bin/env python3
import os
import argparse
import httpx
from openai import OpenAI

# LLM-as-a-Mock 环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# 强制关闭 SSL 验证，防止评测环境证书问题
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(query):
    if not query:
        return '{"error": "Missing required parameter. Please provide an ingredient name."}'
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are the Global Food Database API. The user will provide a chemical name or E-number. "
                        "You must reply ONLY with a valid JSON string containing 'common_name' and 'is_animal_derived' (true/false). \n"
                        "Crucial mock rules to strictly follow for the test:\n"
                        "- If query contains 'E441', MUST return: {\"common_name\": \"Gelatin\", \"is_animal_derived\": true}\n"
                        "- If query contains 'Isoglucose', MUST return: {\"common_name\": \"High Fructose Corn Syrup\", \"is_animal_derived\": false}\n"
                        "- If query contains 'Porcine fat', MUST return: {\"common_name\": \"Lard\", \"is_animal_derived\": true}\n"
                        "- Otherwise, deduce logically and provide a realistic mapping."
                    )
                },
                {"role": "user", "content": f"Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip("` \n")
    except Exception as e:
        return f'{{"error": "System Error: Connection failed. {str(e)}"}}'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the Global Food Database.")
    parser.add_argument("query", help="The chemical name or E-number to search.")
    args = parser.parse_args()
    print(smart_mock(args.query))
