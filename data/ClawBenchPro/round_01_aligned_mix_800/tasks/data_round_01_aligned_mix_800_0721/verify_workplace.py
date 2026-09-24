import os
import sys
import json
import httpx
import re
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    records_file = os.path.join(workspace, "records", "inbox_export.csv")
    
    score_details = []
    total_score = 0

    # 1. 检查目录和文件是否存在 (10 points)
    leads_path = os.path.join(deliverables_dir, "wellness_leads.txt")
    revenue_path = os.path.join(deliverables_dir, "soil_monitor_revenue.txt")
    
    dir_exists = os.path.exists(deliverables_dir)
    leads_exists = os.path.exists(leads_path)
    rev_exists = os.path.exists(revenue_path)

    if dir_exists and leads_exists and rev_exists:
        score_details.append({"item": "文件存在性检查", "score": 10, "max_score": 10, "passed": True, "reason": "所有要求的文件和目录均已生成"})
        total_score += 10
    else:
        score_details.append({"item": "文件存在性检查", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失文件或目录。deliverables: {dir_exists}, leads: {leads_exists}, revenue: {rev_exists}"})

    # 2. 验证 wellness_leads.txt 内容 (40 points)
    # 预期逻辑：关键词 "health", "wellness", "garden"
    # Alice: garden (YES)
    # Bob: wellness (YES)
    # Charlie: none (NO)
    # Diana: Health (YES)
    # Edward: none (NO)
    # Frank: none (NO)
    expected_emails = {"alice@example.com", "bob@example.com", "diana@mail.com"}
    
    if leads_exists:
        try:
            with open(leads_path, "r") as f:
                content = f.read().strip().splitlines()
                actual_emails = {email.strip() for email in content if email.strip()}
            
            if actual_emails == expected_emails:
                score_details.append({"item": "客户线索提取准确性", "score": 40, "max_score": 40, "passed": True, "reason": "成功提取了所有匹配关键词且无冗余的邮箱"})
                total_score += 40
            elif actual_emails.issubset(expected_emails) and len(actual_emails) > 0:
                score_details.append({"item": "客户线索提取准确性", "score": 20, "max_score": 40, "passed": False, "reason": f"提取不全，预期 {expected_emails}, 实际 {actual_emails}"})
                total_score += 20
            else:
                score_details.append({"item": "客户线索提取准确性", "score": 0, "max_score": 40, "passed": False, "reason": f"提取结果错误，实际内容：{actual_emails}"})
        except Exception as e:
            score_details.append({"item": "客户线索文件解析失败", "score": 0, "max_score": 40, "passed": False, "reason": str(e)})

    # 3. 验证 soil_monitor_revenue.txt 内容 (50 points)
    # 逻辑：Smart Soil Monitor 的订单
    # 1001: 2 * 25 = 50
    # 1003: 1 * 25 = 25
    # 1005: 3 * 25 = 75
    # 1006: 0 * 25 = 0 (Quantity is 0, should not impact or results in 0)
    # Total = 50 + 25 + 75 = 150
    if rev_exists:
        try:
            with open(revenue_path, "r") as f:
                rev_content = f.read().strip()
                # 使用正则提取数字
                numbers = re.findall(r"[-+]?\d*\.\d+|\d+", rev_content.replace(',', ''))
                if numbers:
                    val = float(numbers[0])
                    if val == 150.0:
                        score_details.append({"item": "收入计算准确性", "score": 50, "max_score": 50, "passed": True, "reason": "收入计算结果完全正确 (150.0)"})
                        total_score += 50
                    elif val == 175.0: # 包含了数量为0但可能没处理好的逻辑
                        score_details.append({"item": "收入计算准确性", "score": 20, "max_score": 50, "passed": False, "reason": "计算结果为175，可能未正确处理数量为0的取消订单或单价解析异常"})
                        total_score += 20
                    else:
                        score_details.append({"item": "收入计算准确性", "score": 0, "max_score": 50, "passed": False, "reason": f"计算结果错误，预期 150.0, 实际得到 {val}"})
                else:
                    score_details.append({"item": "收入计算准确性", "score": 0, "max_score": 50, "passed": False, "reason": "无法在文件中找到数值结果"})
        except Exception as e:
            score_details.append({"item": "收入文件解析失败", "score": 0, "max_score": 50, "passed": False, "reason": str(e)})

    # 输出最终评分
    output = {
        "total_score": int(total_score),
        "details": score_details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
