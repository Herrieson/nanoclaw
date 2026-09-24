import os
import sys
import json
import httpx
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    
    # 定义预期结果数据
    # E001: Log 42h, Sched 40h (Diff 5% <= 10%, Valid)
    # E002: Log 25h, Sched 20h (Diff 25% > 10%, Flagged)
    # E003: Log 30h, Sched 30h (Valid)
    # E004: Log 5h, Sched None (Ghost)
    # E005: Log None, Sched 8h
    
    # 1. 检查交付文件是否存在 (10分)
    payroll_path = os.path.join(workspace, "deliverables/payroll_final.json")
    audit_path = os.path.join(workspace, "deliverables/audit_summary.txt")
    
    payroll_exists = os.path.exists(payroll_path)
    audit_exists = os.path.exists(audit_path)
    
    score_details.append({
        "item": "文件交付完整性",
        "score": 10 if payroll_exists and audit_exists else (5 if payroll_exists or audit_exists else 0),
        "max_score": 10,
        "passed": payroll_exists and audit_exists,
        "reason": f"Payroll: {payroll_exists}, Audit: {audit_exists}"
    })

    # 2. 验证 payroll_final.json 的数值准确性 (50分)
    payroll_score = 0
    if payroll_exists:
        try:
            with open(payroll_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 必须包含 E001, E002, E003
            ids = [item.get("id") for item in data]
            valid_ids = {"E001", "E002", "E003"}
            id_check = all(eid in ids for eid in valid_ids)
            if id_check: payroll_score += 10
            
            # 核心数值检查 (E001: 42h, E002: 25h, E003: 30h)
            # 检查 E001 是否正确计算总薪水 (假设 Cloud HR API 返回的时薪为预设值)
            # 由于 API 模拟，我们重点检查其 valid_hours 的提取
            e001_item = next((i for i in data if i['id'] == "E001"), {})
            e002_item = next((i for i in data if i['id'] == "E002"), {})
            
            if e001_item.get("valid_hours") == 42: payroll_score += 15
            if e002_item.get("valid_hours") == 25: payroll_score += 15
            
            # 检查是否包含 total_payout 字段且为数值
            if all(isinstance(i.get("total_payout"), (int, float)) for i in data):
                payroll_score += 10
                
        except Exception as e:
            payroll_score = 0
            print(f"JSON 解析错误: {e}")
            
    score_details.append({
        "item": "薪资结算单数值准确性",
        "score": payroll_score,
        "max_score": 50,
        "passed": payroll_score >= 40,
        "reason": f"最终得分 {payroll_score}/50"
    })

    # 3. 验证 audit_summary.txt 的业务逻辑 (40分)
    audit_score = 0
    if audit_exists:
        with open(audit_path, 'r', encoding='utf-8') as f:
            audit_content = f.read()
        
        # 3.1 检查幽灵员工 E004 (20分)
        if llm_judge_content("这份审计报告是否明确指出了 'E004' 是没有排班却有打卡记录的‘幽灵员工’？", audit_content):
            audit_score += 20
        
        # 3.2 检查超时员工 E002 (20分)
        if llm_judge_content("这份审计报告是否明确指出了 'E002' 因为打卡时长超过排班时长的 10% 而被标记为异常？", audit_content):
            audit_score += 20
            
    score_details.append({
        "item": "审计报告业务逻辑合规性",
        "score": audit_score,
        "max_score": 40,
        "passed": audit_score == 40,
        "reason": f"大模型审计结果: {audit_score}/40"
    })

    # 计算总分
    total_score = sum(d['score'] for d in score_details)
    
    # 写入结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
