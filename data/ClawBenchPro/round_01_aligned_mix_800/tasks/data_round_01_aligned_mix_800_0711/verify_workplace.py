import os
import sys
import json
import httpx
import glob
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型判决接口：严格返回 bool"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict clinical data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[Report Content]:\n{file_content}"}
            ],
            temperature=0
        )
        answer = response.choices[0].message.content.strip().lower()
        return "yes" in answer
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []
    
    audit_dir = os.path.join(workspace, "audit_reports")
    
    # 1. 检查目录是否存在 (10分)
    if os.path.isdir(audit_dir):
        details.append({"item": "检查目录 audit_reports 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 audit_reports 存在"})
        total_score += 10
    else:
        details.append({"item": "检查目录 audit_reports 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录 audit_reports 不存在"})
        
    # 2. 检查是否有报告文件 (10分)
    report_files = []
    if os.path.isdir(audit_dir):
        report_files = glob.glob(os.path.join(audit_dir, "*.*"))
        
    if report_files:
        details.append({"item": "检查报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": f"找到报告文件: {len(report_files)} 个"})
        total_score += 10
    else:
        details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到任何报告文件"})
        
    # 提取所有报告文本进行综合审核
    report_content = ""
    for f_path in report_files:
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                report_content += f.read() + "\n"
        except Exception:
            pass

    # 若没有内容，后续 LLM 检查均失败
    if not report_content.strip():
        report_content = "EMPTY REPORT"

    # 3. LLM 检查：是否识别出不在名单的异常患者 (20分)
    prompt_1 = "Does the report explicitly identify that patient 'P006' received medications despite NOT being on the Master List?"
    if llm_judge_content(prompt_1, report_content):
        details.append({"item": "识别异常发药患者(P006)", "score": 20, "max_score": 20, "passed": True, "reason": "大模型确认报告指出了 P006 的异常。"})
        total_score += 20
    else:
        details.append({"item": "识别异常发药患者(P006)", "score": 0, "max_score": 20, "passed": False, "reason": "报告遗漏或未能正确指出不在名单的 P006。"})

    # 4. LLM 检查：是否识别出名单内缺药的患者 (20分)
    prompt_2 = "Does the report state that any patient from the Master List (e.g., P003, or others) missed their mandatory medications?"
    if llm_judge_content(prompt_2, report_content):
        details.append({"item": "识别漏药患者", "score": 20, "max_score": 20, "passed": True, "reason": "大模型确认报告指出了名单内有患者漏药。"})
        total_score += 20
    else:
        details.append({"item": "识别漏药患者", "score": 0, "max_score": 20, "passed": False, "reason": "报告未指出漏发药物的名单内患者。"})

    # 5. LLM 检查：精确的 Heparin 用量计算 (20分)
    prompt_3 = "Does the report explicitly state that the EXACT total dosage of Heparin administered is 32,500 (or 32500) units?"
    if llm_judge_content(prompt_3, report_content):
        details.append({"item": "核算 Heparin 总剂量", "score": 20, "max_score": 20, "passed": True, "reason": "大模型确认报告精确算出了 32500 的总剂量。"})
        total_score += 20
    else:
        details.append({"item": "核算 Heparin 总剂量", "score": 0, "max_score": 20, "passed": False, "reason": "报告计算错误，未得出 32500 的确切结论。"})

    # 6. LLM 检查：超量告警标志 (20分)
    prompt_4 = "Does the report explicitly FLAG, WARN, or HIGHLIGHT that the Heparin dosage exceeded the floor stock threshold of 25,000 units?"
    if llm_judge_content(prompt_4, report_content):
        details.append({"item": "Heparin 超量告警", "score": 20, "max_score": 20, "passed": True, "reason": "大模型确认报告包含了阈值超标的显式告警。"})
        total_score += 20
    else:
        details.append({"item": "Heparin 超量告警", "score": 0, "max_score": 20, "passed": False, "reason": "报告未针对超出 25000 阈值提供明确告警。"})

    # 写入最终得分文件
    score_data = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
