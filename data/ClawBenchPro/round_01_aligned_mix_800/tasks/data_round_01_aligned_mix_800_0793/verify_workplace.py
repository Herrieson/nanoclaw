import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    # 此函数为检测非结构化文本的统一接口
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    
    suspects_path = os.path.join(workspace, "investigation", "suspects.json")
    
    # Check 1: File existence (10 pts)
    if os.path.isfile(suspects_path):
        results.append({"item": "检查文件 suspects.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        results.append({"item": "检查文件 suspects.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)
        return

    # Check 2: Valid JSON and Schema (10 pts)
    try:
        with open(suspects_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        valid_schema = True
        if not isinstance(data, dict):
            valid_schema = False
        else:
            for k, v in data.items():
                if not isinstance(v, dict) or "total_minutes" not in v or "is_approved" not in v:
                    valid_schema = False
                    break
        
        if valid_schema:
            results.append({"item": "检查 JSON 格式与 Schema 合法性", "score": 10, "max_score": 10, "passed": True, "reason": "Schema 合法"})
            total_score += 10
        else:
            results.append({"item": "检查 JSON 格式与 Schema 合法性", "score": 0, "max_score": 10, "passed": False, "reason": "数据结构不符合要求"})
            data = None # Prevent further checks
    except Exception as e:
        results.append({"item": "检查 JSON 格式与 Schema 合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        data = None
        
    if data is None:
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)
        return

    # Check 3: Exact correct suspects identified (20 pts)
    # The suspects should be exactly Bob and Eve.
    # Alice was in The Vault but not during off-hours (14:00-14:15).
    # Charlie was in Storefront. Zack was in Breakroom.
    expected_suspects = {"Bob", "Eve"}
    actual_suspects = set(data.keys())
    
    if actual_suspects == expected_suspects:
        results.append({"item": "检查目标嫌疑人识别正确性 (无多抓、无漏抓)", "score": 20, "max_score": 20, "passed": True, "reason": "准确找出了 Bob 和 Eve"})
        total_score += 20
    else:
        results.append({"item": "检查目标嫌疑人识别正确性", "score": 0, "max_score": 20, "passed": False, "reason": f"预期人员: {expected_suspects}, 实际人员: {actual_suspects}"})

    # Check 4: total_minutes accuracy (30 pts)
    # Bob: 30 minutes (23:00 to 23:30)
    # Eve: 45 + 10 = 55 minutes (01:15-02:00, 04:00-04:10)
    minutes_score = 0
    if "Bob" in data and data["Bob"].get("total_minutes") == 30:
        minutes_score += 15
    if "Eve" in data and data["Eve"].get("total_minutes") == 55:
        minutes_score += 15
        
    if minutes_score == 30:
        results.append({"item": "检查夜间滞留总时长计算准确性", "score": 30, "max_score": 30, "passed": True, "reason": "Bob 和 Eve 的时长计算全对 (30, 55)"})
    else:
        results.append({"item": "检查夜间滞留总时长计算准确性", "score": minutes_score, "max_score": 30, "passed": False, "reason": f"部分时长计算错误。Bob需为30，Eve需为55。"})
    total_score += minutes_score

    # Check 5: is_approved resolution (30 pts)
    # Bob: True, Eve: False
    approved_score = 0
    if "Bob" in data and data["Bob"].get("is_approved") is True:
        approved_score += 15
    if "Eve" in data and data["Eve"].get("is_approved") is False:
        approved_score += 15
        
    if approved_score == 30:
        results.append({"item": "检查授权员工名单比对准确性", "score": 30, "max_score": 30, "passed": True, "reason": "名单比对全对 (Bob: True, Eve: False)"})
    else:
        results.append({"item": "检查授权员工名单比对准确性", "score": approved_score, "max_score": 30, "passed": False, "reason": "True/False 授权状态鉴定有误"})
    total_score += approved_score

    # 结果持久化
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
