import os
import sys
import json
import httpx
import re
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    
    admin_dir = os.path.join(workspace, "admin_delivery")
    
    # 1. 检查目录 (10)
    has_dir = os.path.isdir(admin_dir)
    results.append({
        "item": "检查目标投递目录是否存在",
        "score": 10 if has_dir else 0,
        "max_score": 10,
        "passed": has_dir,
        "reason": "目录 admin_delivery 存在" if has_dir else "目录 admin_delivery 缺失"
    })
    total_score += 10 if has_dir else 0

    # 2. 检查报告生成 (10)
    report_content = ""
    has_report = False
    if has_dir:
        files = os.listdir(admin_dir)
        report_files = [f for f in files if f.endswith(('.txt', '.md', '.csv', '.json'))]
        if report_files:
            has_report = True
            with open(os.path.join(admin_dir, report_files[0]), "r", encoding="utf-8") as f:
                report_content = f.read()
    
    results.append({
        "item": "检查是否生成了最终报告文件",
        "score": 10 if has_report else 0,
        "max_score": 10,
        "passed": has_report,
        "reason": "找到报告文件" if has_report else "未找到任何文本类报告"
    })
    total_score += 10 if has_report else 0

    if not has_report:
        # 兜底写入0分其余项
        results.append({"item": "剔除非Charity患者", "score": 0, "max_score": 25, "passed": False, "reason": "无文件无法检查"})
        results.append({"item": "包含正确Charity患者", "score": 0, "max_score": 25, "passed": False, "reason": "无文件无法检查"})
        results.append({"item": "大模型语义检查", "score": 0, "max_score": 30, "passed": False, "reason": "无文件无法检查"})
    else:
        # 3. 严格剔除非 Charity 患者 (25)
        # P-001 和 P-007 是非 Charity，不能出现在最终核算列表中。
        has_p001 = "P-001" in report_content
        has_p007 = "P-007" in report_content
        exclude_passed = not (has_p001 or has_p007)
        results.append({
            "item": "严格过滤非慈善项目患者",
            "score": 25 if exclude_passed else 0,
            "max_score": 25,
            "passed": exclude_passed,
            "reason": "成功剔除P-001和P-007" if exclude_passed else "报告错误地包含了P-001或P-007(非Charity患者)"
        })
        total_score += 25 if exclude_passed else 0

        # 4. 包含确定的 Charity 患者 (25)
        # P-002, P-003, P-006 应该被包含。
        has_p002 = "P-002" in report_content
        has_p003 = "P-003" in report_content
        has_p006 = "P-006" in report_content
        include_count = sum([has_p002, has_p003, has_p006])
        include_score = int((include_count / 3) * 25)
        results.append({
            "item": "准确提取确定的慈善项目患者",
            "score": include_score,
            "max_score": 25,
            "passed": include_count == 3,
            "reason": f"找到了 {include_count}/3 个已知的 Charity 患者 (P-002, P-003, P-006)"
        })
        total_score += include_score

        # 5. 大模型评估专业性与总计核算 (30)
        llm_prompt = (
            "Evaluate the provided doctor's patient summary report. "
            "1. Does it explicitly calculate and clearly present the GRAND TOTAL of time/hours spent? "
            "2. Is the tone clean, professional, and suitable for hospital administration delivery? "
            "Answer 'YES' only if BOTH criteria are met clearly."
        )
        llm_passed = llm_judge_content(llm_prompt, report_content)
        results.append({
            "item": "大模型检查格式专业性与时间加总",
            "score": 30 if llm_passed else 0,
            "max_score": 30,
            "passed": llm_passed,
            "reason": "格式清晰专业且包含了总计时间" if llm_passed else "缺乏总时长或表述不够专业"
        })
        total_score += 30 if llm_passed else 0

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
