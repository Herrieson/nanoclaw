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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []

    report_dir = os.path.join(workspace, "audit_reports")
    report_content = ""

    # 1. 结构与格式确定性检查 (10 分)
    if os.path.isdir(report_dir):
        files = os.listdir(report_dir)
        valid_files = [f for f in files if os.path.isfile(os.path.join(report_dir, f))]
        
        if valid_files:
            details.append({"item": "检查报告目录和文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建 audit_reports 目录并生成文件"})
            total_score += 10
            
            for f in valid_files:
                with open(os.path.join(report_dir, f), "r", encoding="utf-8") as file:
                    report_content += file.read() + "\n"
        else:
            details.append({"item": "检查报告目录和文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "audit_reports 目录存在但未找到任何报告文件"})
    else:
        details.append({"item": "检查报告目录和文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 audit_reports 目录"})

    # 如果报告内容为空，直接略过后续的 LLM 验证，得分保持为 0
    if not report_content.strip():
        details.extend([
            {"item": "总结专业度", "score": 0, "max_score": 10, "passed": False, "reason": "报告内容为空，无法进行语义评估"},
            {"item": "核算肝素总剂量", "score": 0, "max_score": 25, "passed": False, "reason": "报告内容为空"},
            {"item": "核对未授权患者(P006)", "score": 0, "max_score": 20, "passed": False, "reason": "报告内容为空"},
            {"item": "指出未按时给药的患者", "score": 0, "max_score": 15, "passed": False, "reason": "报告内容为空"},
            {"item": "政策阈值超标警告", "score": 0, "max_score": 20, "passed": False, "reason": "报告内容为空"}
        ])
    else:
        # 2. LLM 检查语义：总结报告的专业度 (10 分)
        prompt_prof = "Evaluate if the text is structured as a professional clinical audit or shift handoff summary report. Answer YES if it looks like a professional summary, NO otherwise."
        if llm_judge_content(prompt_prof, report_content):
            details.append({"item": "总结专业度", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定具备专业审计报告的格式与语气"})
            total_score += 10
        else:
            details.append({"item": "总结专业度", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定报告缺乏专业的结构或语气"})

        # 3. LLM 检查语义：计算肝素总使用量 (25 分)
        prompt_hep = "Evaluate if the report explicitly calculates and states that the TOTAL Heparin usage/dosage is exactly 32,500 (or 32500) units. If it clearly states 32,500 as the total, answer YES. If it states any other number or omits it, answer NO."
        if llm_judge_content(prompt_hep, report_content):
            details.append({"item": "核算肝素总剂量", "score": 25, "max_score": 25, "passed": True, "reason": "准确计算出肝素总量为 32500 单位"})
            total_score += 25
        else:
            details.append({"item": "核算肝素总剂量", "score": 0, "max_score": 25, "passed": False, "reason": "未能准确计算出肝素总剂量为 32500，或未在报告中明确说明"})

        # 4. LLM 检查语义：识别未授权的用药患者 P006 (20 分)
        prompt_p006 = "Evaluate if the report identifies patient 'P006' as a critical discrepancy, specifically noting that P006 received medication but is NOT on the authorized Patient Master List. Answer YES if it identifies P006 as unlisted/unauthorized, NO otherwise."
        if llm_judge_content(prompt_p006, report_content):
            details.append({"item": "核对未授权患者(P006)", "score": 20, "max_score": 20, "passed": True, "reason": "成功识别出不在 Master List 中的 P006 接收了给药"})
            total_score += 20
        else:
            details.append({"item": "核对未授权患者(P006)", "score": 0, "max_score": 20, "passed": False, "reason": "未能识别出 P006 为未在名单中的异常患者"})

        # 5. LLM 检查语义：识别出延迟/错过0800给药的患者 (15 分)
        prompt_missed = "Evaluate if the report identifies discrepancies regarding the 08:00 (0800) medication schedule, specifically pointing out that patients like P004 or P005 missed their mandatory 08:00 meds (or received them late). Answer YES if it does, NO otherwise."
        if llm_judge_content(prompt_missed, report_content):
            details.append({"item": "指出未按时给药的患者", "score": 15, "max_score": 15, "passed": True, "reason": "明确指出了 P004 和 P005 错过了 08:00 的给药时间"})
            total_score += 15
        else:
            details.append({"item": "指出未按时给药的患者", "score": 0, "max_score": 15, "passed": False, "reason": "未发现或未指出 P004 和 P005 的给药时间差异"})

        # 6. LLM 检查语义：与医院阈值政策对照并警告 (20 分)
        prompt_policy = "Evaluate if the report explicitly compares the total Heparin usage against the policy threshold of 25,000 units, clearly states that the threshold was exceeded, and mentions flagging this to the Chief Nursing Officer. Answer YES if it includes these points, NO otherwise."
        if llm_judge_content(prompt_policy, report_content):
            details.append({"item": "政策阈值超标警告", "score": 20, "max_score": 20, "passed": True, "reason": "正确应用了 25000 单位的阈值政策并发出超标通告"})
            total_score += 20
        else:
            details.append({"item": "政策阈值超标警告", "score": 0, "max_score": 20, "passed": False, "reason": "没有结合 25000 的阈值政策，或未提出 Chief Nursing Officer 警告"})

    # 输出结果文件
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
if __name__ == "__main__":
    main()
