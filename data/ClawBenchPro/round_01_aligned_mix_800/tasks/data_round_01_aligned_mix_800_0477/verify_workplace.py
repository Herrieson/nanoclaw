import os
import sys
import json
import csv
import glob
import httpx
from openai import OpenAI

# 配置常量
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
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def run_verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "final_audit/audit_report.json")
    details = []
    total_score = 0

    # 1. 基础文件结构检查 (10分)
    if os.path.exists(report_path):
        details.append({"item": "文件生成检查", "score": 10, "max_score": 10, "passed": True, "reason": "final_audit/audit_report.json 已生成"})
        total_score += 10
    else:
        details.append({"item": "文件生成检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到审计报告文件"})
        # 如果文件不存在，后续检查无法进行，直接写入结果
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # 加载报告内容
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        details.append({"item": "JSON 格式解析", "score": 0, "max_score": 10, "passed": False, "reason": f"无法解析 JSON: {str(e)}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return
    
    details.append({"item": "JSON 格式解析", "score": 10, "max_score": 10, "passed": True, "reason": "格式合法"})
    total_score += 10

    # 2. Ghost 识别准确性 (30分)
    # 标准答案参考：Marcus Vane (Claim), Ghost-7 (Log), Unknown Scavenger (Log)
    # 必须排除：Bernice Thompson, Althea Richards, Cedric Miller, Darnell Williams, Elena Vance, Garrick Thorne, Sheila Reed (DEPRECATED)
    ghosts = data.get("ghosts", [])
    expected_ghosts = {"Marcus Vane", "Ghost-7"} # 最核心的两个
    provided_ghosts = set(ghosts)
    
    found_core = expected_ghosts.issubset(provided_ghosts)
    noise_in_ghosts = any(name in provided_ghosts for name in ["Bernice Thompson", "Sheila Reed", "Darnell Williams"])
    
    if found_core and not noise_in_ghosts:
        details.append({"item": "Ghost 识别准确性", "score": 30, "max_score": 30, "passed": True, "reason": "准确识别了核心 Ghost 且未包含合法人员或废弃数据"})
        total_score += 30
    elif found_core:
        details.append({"item": "Ghost 识别准确性", "score": 15, "max_score": 30, "passed": False, "reason": "识别了核心 Ghost 但结果中包含脏数据"})
        total_score += 15
    else:
        details.append({"item": "Ghost 识别准确性", "score": 0, "max_score": 30, "passed": False, "reason": "未准确识别核心 Ghost"})

    # 3. 薪酬计算与过滤 (30分)
    # Bernice: 15.5 + 26.0 = 41.5 -> $3527.5
    # Althea: 12.0 -> $1020
    # Elena: 5.0 -> $425
    # Darnell Williams: 应为 0 (因为他的记录在 _VOID_ 文件中)
    payroll = data.get("payroll", {})
    # 检查 Bernice 的金额 (85 * 41.5 = 3527.5)
    bernice_pay = payroll.get("Bernice Thompson")
    althea_pay = payroll.get("Althea Richards")
    darnell_pay = payroll.get("Darnell Williams")
    
    payroll_score = 0
    reasons = []
    if bernice_pay == 3527.5:
        payroll_score += 15
    else:
        reasons.append(f"Bernice 薪酬错误: 预期 3527.5, 实际 {bernice_pay}")
        
    if althea_pay == 1020:
        payroll_score += 10
    else:
        reasons.append(f"Althea 薪酬错误")

    if darnell_pay is None or darnell_pay == 0:
        payroll_score += 5
    else:
        reasons.append("未能过滤 _VOID_ 文件中的 Darnell 记录")
        
    details.append({
        "item": "薪酬计算与过滤(Q3 & VOID)", 
        "score": payroll_score, 
        "max_score": 30, 
        "passed": payroll_score == 30, 
        "reason": "; ".join(reasons) if reasons else "薪酬计算完全正确"
    })
    total_score += payroll_score

    # 4. 安全指数 (Fatigue Index) 触发 (20分)
    # Bernice Thompson 总时长 41.5 > 40，必须为 CRITICAL
    safety = data.get("safety", [])
    # 假设 safety 是个列表包含对象，或 payroll 里的字段。题目要求是一个 report.json。
    # 我们通过 LLM 来灵活判断 report 的 safety 部分是否符合要求
    safety_prompt = "Does the report correctly identify 'Bernice Thompson' as having a 'fatigue_index' set to 'CRITICAL' because her total hours exceed 40?"
    if llm_judge_content(safety_prompt, json.dumps(data)):
        details.append({"item": "安全疲劳指数检查", "score": 20, "max_score": 20, "passed": True, "reason": "Bernice Thompson 已被标记为 CRITICAL"})
        total_score += 20
    else:
        details.append({"item": "安全疲劳指数检查", "score": 0, "max_score": 20, "passed": False, "reason": "未正确标记超负荷人员"})

    # 5. 总分汇总
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(total_score), "details": details}, f)

if __name__ == "__main__":
    run_verify()
