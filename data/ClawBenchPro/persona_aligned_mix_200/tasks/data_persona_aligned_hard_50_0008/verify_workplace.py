import os
import sys
import json
import httpx
from openai import OpenAI

# ---------------------------------------------------------
# [强制 API 规范]：即使当前采用严格的代码确定性验证，
# 也必须保留大模型检测基建，以备未来对非结构化文件进行校验。
# ---------------------------------------------------------
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """用于检测非结构化文本的统一接口"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

# ---------------------------------------------------------
# 核心验证逻辑：防御性编程，对格式、键值、结果准确度分级剥离
# ---------------------------------------------------------
def verify(workspace):
    details = []
    total_score = 0
    
    report_path = os.path.join(workspace, "reports", "bottleneck.json")
    
    # 考核项 1: 文件定位与留存 (10分)
    if os.path.exists(report_path):
        details.append({
            "item": "检查目标文件是否在规范路径生成", 
            "score": 10, "max_score": 10, "passed": True, 
            "reason": "成功定位到 reports/bottleneck.json"
        })
        total_score += 10
    else:
        details.append({
            "item": "检查目标文件是否在规范路径生成", 
            "score": 0, "max_score": 10, "passed": False, 
            "reason": "未能找到交差文件 reports/bottleneck.json"
        })
        return total_score, details

    # 考核项 2: 数据结构纯净度校验 (20分)
    # 防御思路：禁止返回携带 markdown 标记的冗余文本（如
