import os
import sys
import json
import httpx
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
    """
    使用 LLM 对自然语言构成的文档进行语义及合规性判定
    """
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."
                },
                {
                    "role": "user", 
                    "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"
                }
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    
    # 1. 检查结果报告是否存在 (10分)
    report_path = os.path.join(workspace, "clean_desk", "emergency_report.md")
    if os.path.exists(report_path):
        results.append({
            "item": "检查目标报告文件是否存在", 
            "score": 10, 
            "max_score": 10, 
            "passed": True, 
            "reason": "emergency_report.md 文件已正确创建于 clean_desk 目录中。"
        })
        total_score += 10
    else:
        results.append({
            "item": "检查目标报告文件是否存在", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": "emergency_report.md 缺失！"
        })
        
    # 2. 检查大面积垃圾清理情况及正常文件的存留 (30分)
    trash_found = 0
    normal_found = 0
    
    for root, dirs, files in os.walk(workspace):
        # 跳过整理完成的工作区目录
        if "clean_desk" in root: 
            continue
        for f in files:
            f_lower = f.lower()
            if f_lower.startswith("lunch_") or f_lower.startswith("receipt_"):
                trash_found += 1
            elif f_lower.startswith("normal_log_"):
                normal_found += 1
                
    # 垃圾清理得分计算 (15分)：存在残留按比例扣分
    trash_score = max(0, 15 - trash_found) 
    trash_passed = trash_score == 15
    results.append({
        "item": "验证大规模垃圾文件是否被彻底清理", 
        "score": trash_score, 
        "max_score": 15, 
        "passed": trash_passed, 
        "reason": f"工作区内残留垃圾文件数量: {trash_found}"
    })
    total_score += trash_score
    
    # 正常文件存留计算 (15分)：共 50 个 normal_log，少一个扣 2 分
    normal_score = max(0, 15 - (50 - normal_found) * 2) if normal_found <= 50 else 15
    normal_passed = normal_found >= 48
    results.append({
        "item": "验证正常文件是否免于被误删", 
        "score": normal_score, 
        "max_score": 15, 
        "passed": normal_passed, 
        "reason": f"未被误删的正常文件数量: {normal_found}/50"
    })
    total_score += normal_score
    
    # 3. 核心事件提取精确度 (42分：共6条隐藏线索，每条7分)
    report_content = ""
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_content = f.read().lower()
        except Exception:
            pass
            
    # 使用极高确定性的子字符串组合探测核心案情是否被遗漏
    targets = [
        {"name": "提取目标 1: 隐藏在深层 JSON 碎片中的锅炉房积水", "keywords": ["boiler", "flooding", "valve"]},
        {"name": "提取目标 2: Log 泄露案情 (Unit 404/Mold)", "keywords": ["unit 404", "mold"]},
        {"name": "提取目标 3: Log 紧急警报案情 (Elevator/Fraying)", "keywords": ["elevator", "fraying", "tower b"]},
        {"name": "提取目标 4: 客户笔记中的燃气泄露 (Gas/Stove)", "keywords": ["gas", "stove"]},
        {"name": "提取目标 5: 客户笔记中的阳台危机 (Balcony/Railing)", "keywords": ["balcony", "railing"]},
        {"name": "提取目标 6: 误导性文件名中的紧急事件 (Roof)", "keywords": ["roof"]}
    ]
    
    if report_content:
        for t in targets:
            found = any(k in report_content for k in t["keywords"])
            t_score = 7 if found else 0
            results.append({
                "item": t["name"], 
                "score": t_score, 
                "max_score": 7, 
                "passed": found, 
                "reason": "成功提取" if found else "丢失该关键事件记录"
            })
            total_score += t_score
    else:
        for t in targets:
            results.append({
                "item": t["name"], 
                "score": 0, 
                "max_score": 7, 
                "passed": False, 
                "reason": "报告文件不存在或无法读取内容"
            })
            
    # 4. LLM 综合排版与幻觉/噪音验证 (18分)
    if report_content and len(report_content.strip()) > 10:
        prompt = (
            "Review this consolidated emergency report. It must be a highly professional markdown document. "
            "CRITICAL: It should ONLY contain legitimate emergencies related to 'LEAK' or 'URGENT' events. "
            "It MUST NOT contain any routine inspections (e.g., 'Routine inspection completed'), nor ANY lunch orders or receipt logs. "
            "Answer YES if it meets all criteria perfectly without hallucination or noise. Answer NO if there's any trash data or poor formatting."
        )
        passed_llm = llm_judge_content(prompt, report_content)
        llm_score = 18 if passed_llm else 0
        results.append({
            "item": "LLM 语义噪音排查及专业度评估", 
            "score": llm_score, 
            "max_score": 18, 
            "passed": passed_llm, 
            "reason": "格式规范且无多余杂音污染" if passed_llm else "格式不达标或混入了普通日志/幻觉数据"
        })
        total_score += llm_score
    else:
        results.append({
            "item": "LLM 语义噪音排查及专业度评估", 
            "score": 0, 
            "max_score": 18, 
            "passed": False, 
            "reason": "无有效内容可供评估"
        })

    # 生成标准得分 JSON 文件
    score_data = {
        "total_score": total_score,
        "details": results
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
