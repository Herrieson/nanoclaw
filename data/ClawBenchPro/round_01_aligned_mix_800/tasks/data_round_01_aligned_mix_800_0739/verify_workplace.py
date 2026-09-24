import os
import sys
import json
import httpx
import re
import csv
from openai import OpenAI

# 配置常量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端
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
    report_path = os.path.join(workspace, "deliverables/audit_report.json")
    score = 0
    details = []

    # 1. 检查文件是否存在与格式合法性 (15分)
    if os.path.exists(report_path):
        score += 5
        details.append({"item": "文件交付", "score": 5, "max_score": 5, "passed": True, "reason": "audit_report.json 存在"})
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            score += 10
            details.append({"item": "JSON格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
        except Exception as e:
            details.append({"item": "JSON格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
            data = None
    else:
        details.append({"item": "文件交付", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 audit_report.json"})
        data = None

    if data:
        # 2. 验证非资格人员名单 (35分)
        # 根据 env_builder: 申请人有 Alice Miller, Bob Chen, Stranger Danger (X), Sarah Jenkins, Linda Goldstein, David Strauss, Malicious User (X)
        # 不在 authorized_volunteers.txt 的是: ["Stranger Danger", "Malicious User"]
        unauthorized = data.get("unauthorized_claimants", [])
        expected_unauthorized = {"Stranger Danger", "Malicious User"}
        actual_unauthorized = set(unauthorized)
        
        if actual_unauthorized == expected_unauthorized:
            score += 35
            details.append({"item": "非资格人员名单识别", "score": 35, "max_score": 35, "passed": True, "reason": "精准识别了所有非资格人员"})
        elif expected_unauthorized.issubset(actual_unauthorized):
            score += 15
            details.append({"item": "非资格人员名单识别", "score": 15, "max_score": 35, "passed": False, "reason": "识别了目标但包含冗余（可能误伤了白名单人员）"})
        elif not actual_unauthorized.isdisjoint(expected_unauthorized):
            score += 10
            details.append({"item": "非资格人员名单识别", "score": 10, "max_score": 35, "passed": False, "reason": "仅部分识别非资格人员"})
        else:
            details.append({"item": "非资格人员名单识别", "score": 0, "max_score": 35, "passed": False, "reason": "完全未能识别非资格人员"})

        # 3. 验证报销金额逻辑 (40分)
        # 计算逻辑：
        # Batch Alpha: Alice (150.50, Ing), Bob (45.00, Equip), Sarah (88.20, Ing). Stranger Danger被剔除.
        # Notes July: Linda (320.00, Equip). David (15.00, Misc -> 剔除). Malicious User被剔除.
        # Final Claims: Bob (12.30, Ing). Alice (25.00, Uniform -> 剔除).
        # 总额 = 150.50 + 45.00 + 88.20 + 320.00 + 12.30 = 616.00
        
        total_amount = data.get("total_approved_amount", -1)
        # 允许极小的浮点误差
        try:
            val = float(total_amount)
            if abs(val - 616.00) < 0.01:
                score += 40
                details.append({"item": "合规报销总额计算", "score": 40, "max_score": 40, "passed": True, "reason": "金额计算完全正确 (616.00)"})
            elif abs(val - 631.00) < 0.01: # 误入了 David 的 15.00 Misc
                score += 10
                details.append({"item": "合规报销总额计算", "score": 10, "max_score": 40, "passed": False, "reason": "金额错误，可能未剔除 Misc 类别"})
            else:
                details.append({"item": "合规报销总额计算", "score": 0, "max_score": 40, "passed": False, "reason": f"金额计算错误，期望 616.00，实际 {val}"})
        except:
            details.append({"item": "合规报销总额计算", "score": 0, "max_score": 40, "passed": False, "reason": "无法解析总金额数值"})

        # 4. 语义检查：是否有明细或审计说明 (10分)
        # 使用 LLM 检查报告是否包含对核算过程的简要说明，符合 Linda 的“挑剔”要求
        content_str = json.dumps(data, ensure_ascii=False)
        is_professional = llm_judge_content("Does this audit report JSON contain a summary or explanation that explains the verification steps or why certain expenses were rejected?", content_str)
        if is_professional:
            score += 10
            details.append({"item": "审计说明专业度", "score": 10, "max_score": 10, "passed": True, "reason": "报告包含必要的审计逻辑说明"})
        else:
            details.append({"item": "审计说明专业度", "score": 0, "max_score": 10, "passed": False, "reason": "报告仅有数据，缺乏对 Linda 要求的细节交代"})

    # 写入结果
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
