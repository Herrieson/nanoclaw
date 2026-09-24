import os
import sys
import json
import glob
import re
import httpx
from openai import OpenAI

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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score_details = []
    total_score = 0
    
    # 1. 检查 deliverables 目录及文件是否存在 (10 分)
    has_file = False
    report_content = ""
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        files = glob.glob(os.path.join(deliverables_dir, "*"))
        files = [f for f in files if os.path.isfile(f)]
        if files:
            has_file = True
            with open(files[0], 'r', encoding='utf-8') as f:
                report_content = f.read()
    
    if has_file and report_content.strip():
        score_details.append({"item": "检查交付目录及文件", "score": 10, "max_score": 10, "passed": True, "reason": "交付物已成功生成"})
        total_score += 10
    else:
        score_details.append({"item": "检查交付目录及文件", "score": 0, "max_score": 10, "passed": False, "reason": "未找到交付物或文件为空"})
        # 写入结果并退出
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 正确的数据：
    # U001: 9000s = 2.5h (Arjun Mehta)
    # U002: 10800s = 3.0h (Priya Sharma)
    # U003: 7200s = 2.0h (Kevin Zhang)
    # U004: 0s = 0.0h (Sarah Jenkins)
    # U005: 0s = 0.0h (Amit Patel)

    text_lower = report_content.lower()

    # 2. 检查有效用户的统计数据计算 (每个15分，共45分)
    expected_data = [
        ("Arjun", "2.5"),
        ("Priya", "3.0"),
        ("Kevin", "2.0")
    ]
    
    for name, hrs in expected_data:
        # 使用正则严格匹配数字，确保不能带有错误数据
        # 寻找诸如 "2.5" 的形式，可能带有 "hours" 或 "hrs"
        match = re.search(rf"{name.lower()}.*?(?<![\d\.])({hrs[0]}\.{hrs[2]}|{hrs[0]})(?![\d\.])", text_lower)
        if match:
            score_details.append({"item": f"检查 {name} 的总时长计算", "score": 15, "max_score": 15, "passed": True, "reason": f"成功提取到正确的时长 {hrs} 小时"})
            total_score += 15
        else:
            score_details.append({"item": f"检查 {name} 的总时长计算", "score": 0, "max_score": 15, "passed": False, "reason": f"未能找到准确的时长 {hrs} 小时，计算可能有误或存在幻觉"})

    # 3. 检查零时长用户的标记 (25分)
    # Sarah 和 Amit 应当被标记为 inactive 且不应具有大于0的时长
    inactive_check_passed = True
    reason_inactive = "成功将 Sarah 和 Amit 标记为 inactive 且排除了错误时长"
    score_inactive = 25

    if "sarah" not in text_lower or "amit" not in text_lower:
         inactive_check_passed = False
         reason_inactive = "未包含所有的映射用户"
         score_inactive = 0
    else:
        if "inactive" not in text_lower:
            inactive_check_passed = False
            reason_inactive = "未按照要求使用 'inactive' 关键字进行标记"
            score_inactive = 0
        else:
            # 确保他们没有被赋予错误的时长
            bad_match = re.search(r"(sarah|amit).*?([1-9]\d*\.?\d*)\s*(hour|hr)", text_lower)
            if bad_match:
                inactive_check_passed = False
                reason_inactive = "将无效用户赋予了错误的时间数值"
                score_inactive = 0

    score_details.append({"item": "检查无效用户的清理与标记", "score": score_inactive, "max_score": 25, "passed": inactive_check_passed, "reason": reason_inactive})
    total_score += score_inactive

    # 4. LLM 判断报告专业性 (20分)
    prompt_text = (
        "Check if the following report is written in a clean, professional tone as requested by a senior developer. "
        "It should NOT sound like an AI assistant's default chatty response (e.g., 'Here is the report you requested!'). "
        "It should look like a formal business or technical summary."
    )
    is_professional = llm_judge_content(prompt_text, report_content)
    if is_professional:
        score_details.append({"item": "专业性检查", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定报告具有专业的商务/技术口吻"})
        total_score += 20
    else:
        score_details.append({"item": "专业性检查", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定报告包含过多啰嗦或非专业用语"})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
