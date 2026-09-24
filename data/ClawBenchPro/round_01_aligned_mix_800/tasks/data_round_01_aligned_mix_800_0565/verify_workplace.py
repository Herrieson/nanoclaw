import os
import sys
import json
import re
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_dir = os.path.join(workspace, "final_report")
    score = 0
    details = []

    # 1. 检查结果目录是否存在 (10分)
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        score += 10
        details.append({"item": "检查结果目录 final_report 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已创建"})
    else:
        details.append({"item": "检查结果目录 final_report 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 final_report 目录"})
        # 如果目录都不存在，后续检查也无法进行，但为了评分逻辑完整，我们继续搜索文件内容

    # 寻找报告文件
    report_files = []
    if os.path.exists(report_dir):
        report_files = [os.path.join(report_dir, f) for f in os.listdir(report_dir) if os.path.isfile(os.path.join(report_dir, f))]
    
    combined_content = ""
    for f_path in report_files:
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                combined_content += f.read() + "\n"
        except:
            pass

    # 2. 验证 Flagged Patient IDs (40分)
    # 正确答案：P-ERR-99, P-ERR-102
    # 错误排除：P-OLD-x (垃圾目录), DEBUG (测试目录)
    target_ids = {"P-ERR-99", "P-ERR-102"}
    found_ids = set()
    if "P-ERR-99" in combined_content: found_ids.add("P-ERR-99")
    if "P-ERR-102" in combined_content: found_ids.add("P-ERR-102")
    
    noise_ids = [f"P-OLD-{i}" for i in range(50)] + ["DEBUG"]
    found_noise = [nid for nid in noise_ids if nid in combined_content]

    id_score = 0
    if "P-ERR-99" in found_ids: id_score += 20
    if "P-ERR-102" in found_ids: id_score += 20
    if found_noise:
        deduction = min(id_score, 20)
        id_score -= deduction
        details.append({"item": "验证异常病人ID", "score": id_score, "max_score": 40, "passed": False, "reason": f"找到了正确ID {found_ids}，但包含了干扰数据 {found_noise[:3]}..."})
    else:
        details.append({"item": "验证异常病人ID", "score": id_score, "max_score": 40, "passed": id_score == 40, "reason": f"找到正确ID: {found_ids}"})
    score += id_score

    # 3. 验证总库存统计 (40分)
    # 计算过程：
    # File A: Lisinopril: 30, Amoxicillin: 10
    # File B: Amoxicillin: 20, Atorvastatin: 90
    # File C: Amoxicillin: 5, Metformin: 60
    # 合计: Amoxicillin: 35, Lisinopril: 30, Atorvastatin: 90, Metformin: 60
    # 重点检查 Amoxicillin 总量 35
    inventory_passed = False
    if "35" in combined_content:
        # 进一步通过 LLM 确认是否为 Amoxicillin 的数量
        MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
        MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
        MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")
        
        try:
            http_client = httpx.Client(verify=False)
            client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
            prompt = "Determine if the following clinic report correctly identifies the total quantity for Amoxicillin as 35. Also check if other meds (Lisinopril: 30, Atorvastatin: 90, Metformin: 60) are aggregated correctly."
            response = client.chat.completions.create(
                model=MOCK_MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a data auditor. Answer ONLY with 'YES' or 'NO'."},
                    {"role": "user", "content": f"{prompt}\n\n[Report Content]:\n{combined_content}"}
                ],
                temperature=0
            )
            if "yes" in response.choices[0].message.content.strip().lower():
                inventory_passed = True
        except Exception as e:
            # Fallback to simple check if LLM fails
            if "35" in combined_content and "Amoxicillin" in combined_content:
                inventory_passed = True

    if inventory_passed:
        score += 40
        details.append({"item": "验证药品库存总量统计", "score": 40, "max_score": 40, "passed": True, "reason": "库存统计正确（Amoxicillin: 35等）"})
    else:
        details.append({"item": "验证药品库存总量统计", "score": 0, "max_score": 40, "passed": False, "reason": "库存统计缺失或数值错误（应含 Amoxicillin: 35）"})

    # 4. 文件格式与整洁度 (10分)
    if len(report_files) > 0 and any(os.path.getsize(f) > 0 for f in report_files):
        score += 10
        details.append({"item": "报告文件生成质量", "score": 10, "max_score": 10, "passed": True, "reason": "报告文件非空且格式清晰"})
    else:
        details.append({"item": "报告文件生成质量", "score": 0, "max_score": 10, "passed": False, "reason": "未生成有效内容"})

    # 写入结果
    result = {
        "total_score": int(score),
        "details": details
    }
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
