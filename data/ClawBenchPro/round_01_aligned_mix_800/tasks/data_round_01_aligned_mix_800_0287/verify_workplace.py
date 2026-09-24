import os
import sys
import json
import httpx
from openai import OpenAI

# 配置环境
workspace = sys.argv[1] if len(sys.argv) > 1 else "."
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化 LLM 客户端
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict administrative auditor. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def verify():
    score = 0
    details = []

    # 1. 检查目录结构 (10分)
    deliverables_path = os.path.join(workspace, "deliverables")
    if os.path.exists(deliverables_path) and os.path.isdir(deliverables_path):
        score += 10
        details.append({"item": "Directory Structure", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables directory created."})
    else:
        details.append({"item": "Directory Structure", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables directory missing."})

    # 2. 检查 JSON 报告的内容与逻辑 (50分)
    json_path = os.path.join(deliverables_path, "violators.json") # 常见命名或通过列表匹配
    if not os.path.exists(json_path):
        # 尝试匹配目录下的任何 json
        json_files = [f for f in os.listdir(deliverables_path) if f.endswith('.json')]
        if json_files:
            json_path = os.path.join(deliverables_path, json_files[0])

    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 校验逻辑：
            # Barnes: Admin 10 -> (10*1.1)/(15+10+11) = 30.5% (Violator)
            # Davis: Admin 6 -> (6.6)/(10+10+6.6) = 24.8% (Violator)
            # 注意：Adams (13.5%) 和 Chen (6.8%) 不应在名单内
            
            # 提取名单里的名字（支持列表或字典格式）
            if isinstance(data, list):
                violators = [str(v).lower() for v in data]
            elif isinstance(data, dict):
                violators = [str(v).lower() for v in data.values()] + [str(k).lower() for k in data.keys()]
            else:
                violators = [str(data).lower()]

            has_barnes = any("barnes" in v for v in violators)
            has_davis = any("davis" in v for v in violators)
            has_others = any("adams" in v or "chen" in v for v in violators)

            if has_barnes and has_davis and not has_others:
                score += 50
                details.append({"item": "Audit Logic (JSON)", "score": 50, "max_score": 50, "passed": True, "reason": "Correctly identified Barnes and Davis with 1.1x multiplier."})
            elif (has_barnes or has_davis) and not has_others:
                score += 25
                details.append({"item": "Audit Logic (JSON)", "score": 25, "max_score": 50, "passed": False, "reason": "Partially identified violators."})
            else:
                details.append({"item": "Audit Logic (JSON)", "score": 0, "max_score": 50, "passed": False, "reason": f"Incorrect violators identified. Found: {violators}"})
        except Exception as e:
            details.append({"item": "Audit Logic (JSON)", "score": 0, "max_score": 50, "passed": False, "reason": f"JSON parse error: {e}"})
    else:
        details.append({"item": "Audit Logic (JSON)", "score": 0, "max_score": 50, "passed": False, "reason": "Compliance JSON report not found."})

    # 3. 检查备忘录 (Markdown) 的语气与内容 (40分)
    md_files = [f for f in os.listdir(deliverables_path) if f.endswith('.md')]
    if md_files:
        md_path = os.path.join(deliverables_path, md_files[0])
        with open(md_path, 'r', encoding='utf-8') as f:
            memo_content = f.read()
        
        # 语义检查 A: 语气是否 Professional but Firm (20分)
        is_firm = llm_judge_content("Is the tone of this memo professional yet firm and direct, calling out inefficiencies without being overly soft or using 'sugarcoating'?", memo_content)
        if is_firm:
            score += 20
            details.append({"item": "Memo Tone", "score": 20, "max_score": 20, "passed": True, "reason": "Tone matches the Analyst's requirement."})
        else:
            details.append({"item": "Memo Tone", "score": 0, "max_score": 20, "passed": False, "reason": "Tone is not firm enough or inappropriate."})

        # 语义检查 B: 是否准确提到违规情况 (20分)
        mentions_audit = llm_judge_content("Does the memo explicitly mention the 20% administrative cap and identify the specific faculty members exceeding it?", memo_content)
        if mentions_audit:
            score += 20
            details.append({"item": "Memo Content Accuracy", "score": 20, "max_score": 20, "passed": True, "reason": "Memo correctly identifies the policy violation details."})
        else:
            details.append({"item": "Memo Content Accuracy", "score": 0, "max_score": 20, "passed": False, "reason": "Memo missing critical violation details."})
    else:
        details.append({"item": "Memo (Markdown)", "score": 0, "max_score": 40, "passed": False, "reason": "Memo file (.md) not found."})

    # 写入最终得分
    output = {"total_score": int(score), "details": details}
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
