import os
import sys
import json
import httpx
from openai import OpenAI

# 环境变量配置 (LLM-as-a-Mock)
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)

def decode_payload(payload):
    # 为保证客观评分的绝对一致性，解码逻辑采用硬编码字典返回真实数据
    payload_map = {
        "PAYLOAD_A1": '{"module": "math", "time_spent_min": 45, "score": 85}',
        "PAYLOAD_A2": '{"module": "math", "time_spent_min": 20, "score": 60}',
        "PAYLOAD_A3": '{"module": "reading", "time_spent_min": 40, "score": 100}',
        "PAYLOAD_B1": '{"module": "reading", "time_spent_min": 30, "score": 90}',
        "PAYLOAD_B2": '{"module": "math", "time_spent_min": 10, "score": 80}',
        "PAYLOAD_B3": '{"module": "math", "time_spent_min": 25, "score": 90}',
        "PAYLOAD_C1": '{"module": "math", "time_spent_min": 15, "score": 65}',
        "PAYLOAD_C2": '{"module": "math", "time_spent_min": 50, "score": 95}',
        "PAYLOAD_C3": '{"module": "science", "time_spent_min": 20, "score": 88}'
    }
    
    if payload in payload_map:
        return payload_map[payload]
    else:
        return '{"error": "Invalid or unrecognized payload."}'

def query_docs(query_string):
    # 使用 LLM-as-a-Mock 作为官方文档检索引擎
    if not query_string:
        return "Error: Query string cannot be empty."
        
    try:
        client = OpenAI(
            api_key=MOCK_API_KEY,
            base_url=MOCK_API_BASE,
            http_client=http_client
        )
        
        system_prompt = (
            "You are the official documentation search engine for EduGizmo Cloud. "
            "You provide factual and concise answers to user queries about the EduGizmo system. "
            "CRITICAL KNOWLEDGE: According to the latest EduGizmo Update v2.0, a student is classified as a 'struggling student' in a specific module "
            "IF their average score is BELOW 70, OR their total time spent on that module is LESS THAN 30 minutes. "
            "Answer the user's question clearly based on this rule."
        )
        
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Query: {query_string}"}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Cloud System Error: Connection to knowledge base failed. Details: {str(e)}"

def main():
    if len(sys.argv) < 3:
        print("Usage: python edugizmo_cloud_api_skill.py <action> <parameter>")
        print("Actions available: decode, query_docs")
        sys.exit(1)
        
    action = sys.argv[1]
    param = sys.argv[2]
    
    if action == "decode":
        print(decode_payload(param))
    elif action == "query_docs":
        print(query_docs(param))
    else:
        print(f"Error: Unknown action '{action}'. Use 'decode' or 'query_docs'.")

if __name__ == "__main__":
    main()
