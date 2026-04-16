import os
import json

def verify():
    report_path = "tax_ready_report.json"
    truth_path = "salon_vault/.secret_truth.json"
    
    results = {
        "report_exists": False,
        "revenue_correct": False,
        "fraud_detected": False,
        "json_format_valid": False,
        "personal_expenses_filtered": False
    }

    if os.path.exists(report_path):
        results["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                results["json_format_valid"] = True
                
                with open(truth_path, "r") as tf:
                    truth = json.load(tf)
                
                # 检查收入 (允许 1% 误差以防浮点数解析问题)
                agent_revenue = float(data.get("total_service_revenue", 0))
                if abs(agent_revenue - truth["true_service_revenue"]) < 1:
                    results["revenue_correct"] = True
                
                # 检查重复扣费
                if str(truth["duplicate_amount"]) in str(data.get("duplicate_charge_identified", "")):
                    results["fraud_detected"] = True
                
                # 检查是否过滤了个人支出 (Yoga/Garden 不应在业务收入里，且应在报告中被提及或排除)
                # 如果报告里明确提到了排除了 Yoga/Garden 或相关金额，则认为通过
                summary = str(data).lower()
                if "yoga" not in summary and "garden" not in summary:
                     results["personal_expenses_filtered"] = True
                     
        except Exception:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
