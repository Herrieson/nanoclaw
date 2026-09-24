import os
import sys
import json
import httpx
import re
from openai import OpenAI

# 强制要求的大模型配置
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
    """检测非结构化文本的统一接口"""
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

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "deliverables", "urgent_field_review.json")
    
    total_score = 0
    details = []

    # 1. 检查目标文件是否存在 (15分)
    file_exists = os.path.exists(target_file)
    if file_exists:
        score = 15
        total_score += score
        details.append({"item": "检查目标文件是否存在", "score": score, "max_score": 15, "passed": True, "reason": f"{target_file} 存在"})
    else:
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": f"未找到 {target_file}"})
        # 文件都不存在，直接结束
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. 检查 JSON 格式合法性 (15分)
    json_data = None
    try:
        with open(target_file, "r") as f:
            content = f.read()
            json_data = json.loads(content)
        score = 15
        total_score += score
        details.append({"item": "JSON格式合法性", "score": score, "max_score": 15, "passed": True, "reason": "文件是合法的JSON结构"})
    except Exception as e:
        details.append({"item": "JSON格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON解析失败: {e}"})
        # JSON非法，无法继续结构化检查
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. 提取其中提及的所有 field_id 进行准确性判定
    content_str = json.dumps(json_data)
    mentioned_fields = set(re.findall(r'Grove_[A-Za-z]+', content_str))
    
    # 违规农田 (True Positives)
    tp_south = "Grove_South" in mentioned_fields
    tp_east = "Grove_East" in mentioned_fields
    tp_central = "Grove_Central" in mentioned_fields
    
    # 无辜农田 (False Positives)
    fp_north = "Grove_North" in mentioned_fields
    fp_west = "Grove_West" in mentioned_fields
    
    has_fp = fp_north or fp_west

    # 3.1 识别出 Grove_South 且没有幻觉 (15分)
    if tp_south and not has_fp:
        score = 15
        total_score += score
        details.append({"item": "准确识别 Grove_South 违规", "score": score, "max_score": 15, "passed": True, "reason": "正确识别出Grove_South且未包含合规地块"})
    else:
        reason = "未识别出Grove_South" if not tp_south else "识别了Grove_South，但包含了不该包含的合规地块(产生了False Positive)，此项清零"
        details.append({"item": "准确识别 Grove_South 违规", "score": 0, "max_score": 15, "passed": False, "reason": reason})

    # 3.2 识别出 Grove_East 且没有幻觉 (15分)
    if tp_east and not has_fp:
        score = 15
        total_score += score
        details.append({"item": "准确识别 Grove_East 违规", "score": score, "max_score": 15, "passed": True, "reason": "正确识别出Grove_East且未包含合规地块"})
    else:
        reason = "未识别出Grove_East" if not tp_east else "识别了Grove_East，但包含了不该包含的合规地块(产生了False Positive)，此项清零"
        details.append({"item": "准确识别 Grove_East 违规", "score": 0, "max_score": 15, "passed": False, "reason": reason})

    # 3.3 识别出 Grove_Central 且没有幻觉 (20分)
    if tp_central and not has_fp:
        score = 20
        total_score += score
        details.append({"item": "准确识别 Grove_Central 违规", "score": score, "max_score": 20, "passed": True, "reason": "正确识别出Grove_Central且未包含合规地块"})
    else:
        reason = "未识别出Grove_Central" if not tp_central else "识别了Grove_Central，但包含了不该包含的合规地块(产生了False Positive)，此项清零"
        details.append({"item": "准确识别 Grove_Central 违规", "score": 0, "max_score": 20, "passed": False, "reason": reason})

    # 4. LLM 验证非结构化描述原因的准确性 (20分)
    prompt_text = (
        "Check if the following JSON explicitly states the correct reasons for these fields:\n"
        "1. Grove_South: MUST mention low/bad pH (or <6.0).\n"
        "2. Grove_East: MUST mention unapproved/unauthorized fertilizer (Synthetic UAN-32).\n"
        "3. Grove_Central: MUST mention BOTH low pH AND unapproved fertilizer (Ammonium Nitrate).\n"
        "If it accurately describes all these reasons, output YES, otherwise output NO."
    )
    llm_passed = llm_judge_content(prompt_text, content_str)
    if llm_passed:
        score = 20
        total_score += score
        details.append({"item": "LLM语义验证违规原因", "score": score, "max_score": 20, "passed": True, "reason": "违规原因描述详尽准确"})
    else:
        details.append({"item": "LLM语义验证违规原因", "score": 0, "max_score": 20, "passed": False, "reason": "违规原因描述不准确、缺失或不符合事实"})

    # 输出分数报告
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify_workplace()
