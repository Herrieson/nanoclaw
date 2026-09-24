import os
import sys
import json
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
    report_path = os.path.join(workspace, "audit_reports", "final_audit.txt")
    
    details = []
    total_score = 0
    
    # 1. 检查文件是否存在
    if os.path.exists(report_path):
        details.append({"item": "检查报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "final_audit.txt 文件存在"})
        total_score += 10
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "final_audit.txt 文件不存在"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 2. 检查幽灵病人 P-9999
    if "P-9999" in content:
        details.append({"item": "识别幽灵病人", "score": 20, "max_score": 20, "passed": True, "reason": "正确提取并报告了幽灵病人 P-9999"})
        total_score += 20
    else:
        details.append({"item": "识别幽灵病人", "score": 0, "max_score": 20, "passed": False, "reason": "报告中遗漏了幽灵病人 P-9999"})

    # 3. 检查遗漏护理 P-3321
    if "P-3321" in content:
        details.append({"item": "识别遗漏护理", "score": 20, "max_score": 20, "passed": True, "reason": "正确提取并报告了遗漏护理病人 P-3321"})
        total_score += 20
    else:
        details.append({"item": "识别遗漏护理", "score": 0, "max_score": 20, "passed": False, "reason": "报告中遗漏了遗漏护理病人 P-3321"})

    # 4. 检查精确剂量 (32500) 以及防混淆 (32600)
    numbers_in_content = re.findall(r'\d+', content)
    has_correct_dose = "32500" in numbers_in_content or "32,500" in content
    has_wrong_dose = "32600" in numbers_in_content or "32,600" in content
    
    if has_correct_dose and not has_wrong_dose:
        details.append({"item": "精确计算 Heparin 总剂量", "score": 25, "max_score": 25, "passed": True, "reason": "正确计算出总量 32500，且成功排除了 Heparin-Flush"})
        total_score += 25
    elif has_wrong_dose:
        details.append({"item": "精确计算 Heparin 总剂量", "score": 0, "max_score": 25, "passed": False, "reason": "计算错误，错误地将 Heparin-Flush 包含在内(计算出32600)"})
    else:
        details.append({"item": "精确计算 Heparin 总剂量", "score": 0, "max_score": 25, "passed": False, "reason": "报告中未找到正确的总剂量数值 (32500)"})

    # 5. 检查警报关键字 RED FLAG
    if "RED FLAG" in content.upper():
        details.append({"item": "触发红色警报", "score": 10, "max_score": 10, "passed": True, "reason": "报告中包含明确的 RED FLAG 警告"})
        total_score += 10
    else:
        details.append({"item": "触发红色警报", "score": 0, "max_score": 10, "passed": False, "reason": "总剂量超标但未触发 RED FLAG"})

    # 6. LLM 语义校验语境，防止瞎拼凑关键词
    prompt_text = "Does this report explicitly explain that P-9999 is a phantom patient (not in registry), P-3321 missed their scheduled care, and the Heparin total exceeds the 25,000 threshold causing a warning? It should read like an audit report, not just random keywords."
    if total_score > 50: # 只有前面的基础信息差不多都有了，才进行语义判别
        if llm_judge_content(prompt_text, content):
            details.append({"item": "LLM 语义验证报告上下文合法性", "score": 15, "max_score": 15, "passed": True, "reason": "大模型判定报告语境自然、逻辑清晰、符合审计说明要求"})
            total_score += 15
        else:
            details.append({"item": "LLM 语义验证报告上下文合法性", "score": 0, "max_score": 15, "passed": False, "reason": "大模型判定报告缺乏合理的业务说明逻辑，疑似堆砌关键词作弊"})
    else:
        details.append({"item": "LLM 语义验证报告上下文合法性", "score": 0, "max_score": 15, "passed": False, "reason": "前置关键指标缺失过多，跳过语义验证"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
