import os
import sys
import json
import httpx
import re
from openai import OpenAI

# 🔒 强制 API 规范
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

def calculate_score():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables")
    score_details = []
    total_score = 0

    # 1. 检查交付物目录与文件是否存在 (10分)
    target_file = None
    if os.path.exists(deliverables_path):
        files = os.listdir(deliverables_path)
        if files:
            target_file = os.path.join(deliverables_path, files[0])
            score_details.append({"item": "交付物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": f"发现文件: {files[0]}"})
            total_score += 10
        else:
            score_details.append({"item": "交付物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录为空"})
    else:
        score_details.append({"item": "交付物目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables 目录"})

    if not target_file:
        # 如果连文件都没有，后续无法进行，直接输出
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        return

    # 读取内容
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        content = ""

    # 2. 检查 Top 3 身份的准确性 (核心：60分，每个 20分)
    # 预期的 Top 3 是 SUBJ_051, SUBJ_182, SUBJ_333
    gold_ids = ["SUBJ_051", "SUBJ_182", "SUBJ_333"]
    found_ids = re.findall(r'SUBJ_\d{3}', content)
    
    correct_count = 0
    for gid in gold_ids:
        if gid in found_ids:
            correct_count += 1
    
    score_ids = correct_count * 20
    score_details.append({
        "item": "Top 3 Subject ID 准确性", 
        "score": score_ids, 
        "max_score": 60, 
        "passed": correct_count == 3, 
        "reason": f"匹配到 {correct_count}/3 个目标 ID"
    })
    total_score += score_ids

    # 3. 检查数值是否存在幻觉/脏数据过滤 (20分)
    # 检查是否包含了诱饵数据（如 SUBJ_007 老鼠，SUBJ_013 退出，或周末 XT-9000 数据）
    decoys = ["SUBJ_007", "SUBJ_013", "SUBJ_200", "SUBJ_201", "SUBJ_222"]
    found_decoys = [d for d in decoys if d in content]
    
    if not found_decoys:
        score_details.append({"item": "脏数据/诱饵过滤", "score": 20, "max_score": 20, "passed": True, "reason": "未发现非法诱饵数据"})
        total_score += 20
    else:
        score_details.append({"item": "脏数据/诱饵过滤", "score": 0, "max_score": 20, "passed": False, "reason": f"包含了被禁用的 Subject ID: {found_decoys}"})

    # 4. 语义格式检查 (10分)
    # 使用 LLM 检查是否清晰列出了 ID 和分数，且语气符合要求（非必须但属于交付质量）
    llm_prompt = "Does this report clearly list the Top 3 Subject IDs and their corresponding MEQ scores? Is it formatted as a clear summary report?"
    if llm_judge_content(llm_prompt, content):
        score_details.append({"item": "内容格式与清晰度", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定报告格式清晰"})
        total_score += 10
    else:
        score_details.append({"item": "内容格式与清晰度", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定报告格式混乱或缺少分数"})

    # 最终输出
    result = {
        "total_score": int(total_score),
        "details": score_details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    calculate_score()
