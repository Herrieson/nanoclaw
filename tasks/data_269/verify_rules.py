import os
import json

def verify():
    report_path = "final_report.json"
    results = {
        "file_exists": False,
        "correct_count": False,
        "correct_avg_price": False,
        "correct_temp_anomalies": False,
        "format_perfect": False
    }

    if not os.path.exists(report_path):
        return results

    results["file_exists"] = True
    
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        
        # 1. 检查记录数 (应该是 4 条 Batch-X74)
        if data.get("affected_records") == 4:
            results["correct_count"] = True
        
        # 2. 检查平均单价 (45.5+120+89.99+210.5)/4 = 116.4975 -> 116.50
        avg_price = data.get("average_unit_price")
        if avg_price and abs(float(avg_price) - 116.50) < 0.1:
            results["correct_avg_price"] = True
            
        # 3. 检查温度异常的时间点 (修正偏移后应该是 12:05 和 12:10)
        anomalies = data.get("temperature_anomalies", [])
        expected_times = ["2023-10-27 12:05:00", "2023-10-27 12:10:00"]
        
        found_times = 0
        for t in expected_times:
            if any(t in str(anomaly) for anomaly in anomalies):
                found_times += 1
        
        if found_times == 2:
            results["correct_temp_anomalies"] = True
            
        results["format_perfect"] = True # 如果能走到这且 JSON 结构清晰
        
    except Exception:
        pass

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
