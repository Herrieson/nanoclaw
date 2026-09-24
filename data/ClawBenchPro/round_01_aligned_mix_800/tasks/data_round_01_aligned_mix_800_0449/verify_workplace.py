import os
import sys
import json
import httpx
import csv
import re
from openai import OpenAI

# 配置环境
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def calculate_ground_truth(workspace):
    """
    重新模拟 Env Builder 的逻辑来生成 Ground Truth，用于对比。
    注意：必须严格遵循 User Prompt 中的过滤逻辑：避开 archive 目录和 .bak 文件。
    """
    gt_total_bleach_used = 0
    gt_total_bleach_lost = 0
    missing_indicators = ["", "N/A", "None", "Unknown", None]

    logs_dir = os.path.join(workspace, "facility_logs")
    if not os.path.exists(logs_dir):
        return None

    for root, dirs, files in os.walk(logs_dir):
        # 排除 archive 文件夹
        if "archive" in root.split(os.sep):
            continue
        
        for file in files:
            # 排除 .bak 文件
            if file.endswith(".bak"):
                continue
            
            file_path = os.path.join(root, file)
            
            try:
                if file.endswith(".csv"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row.get("Item") == "Bleach":
                                q = int(row.get("Quantity", 0))
                                gt_total_bleach_used += q
                                if row.get("Room") in missing_indicators:
                                    gt_total_bleach_lost += q
                
                elif file.endswith(".json"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for row in data:
                            if row.get("item") == "Bleach":
                                q = int(row.get("amount", 0))
                                gt_total_bleach_used += q
                                if row.get("room_no") in missing_indicators:
                                    gt_total_bleach_lost += q
                
                elif file.endswith(".txt"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            # Item: Bleach | Qty: 2 | Room: 101
                            match = re.search(r"Item:\s*(.*?)\s*\|\s*Qty:\s*(\d+)\s*\|\s*Room:\s*(.*)", line)
                            if match:
                                item, qty, room = match.groups()
                                if item.strip() == "Bleach":
                                    q = int(qty)
                                    gt_total_bleach_used += q
                                    if room.strip() in missing_indicators:
                                        gt_total_bleach_lost += q
            except:
                continue

    # 读取库存
    try:
        with open(os.path.join(workspace, "inventory/stock_Nov_30.json"), "r") as f:
            start_stock = json.load(f)["Bleach"]
        with open(os.path.join(workspace, "inventory/stock_Dec_31.json"), "r") as f:
            end_stock = json.load(f)["Bleach"]
        
        gt_discrepancy = gt_total_bleach_used - (start_stock - end_stock)
    except:
        gt_discrepancy = 0

    return {
        "total_bleach_used": gt_total_bleach_used,
        "total_bleach_lost_in_logs": gt_total_bleach_lost,
        "inventory_discrepancy": gt_discrepancy
    }

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_file = "workplace_score.json"
    results = {"total_score": 0, "details": []}
    
    report_path = os.path.join(workspace, "reports/final_audit.json")
    
    # 1. 检查结果文件是否存在 (10分)
    if not os.path.exists(report_path):
        results["details"].append({"item": "文件生成检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 reports/final_audit.json"})
    else:
        results["details"].append({"item": "文件生成检查", "score": 10, "max_score": 10, "passed": True, "reason": "报告文件已生成"})
        
        # 2. 检查 JSON 格式合法性 (10分)
        try:
            with open(report_path, "r") as f:
                agent_data = json.load(f)
            results["details"].append({"item": "JSON格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
            
            # 准备对比数据
            gt = calculate_ground_truth(workspace)
            
            if gt:
                # 3. 检查 total_bleach_used (30分)
                a_used = agent_data.get("total_bleach_used")
                if a_used == gt["total_bleach_used"]:
                    results["details"].append({"item": "Bleach消耗总量计算", "score": 30, "max_score": 30, "passed": True, "reason": "数值完全匹配"})
                else:
                    results["details"].append({"item": "Bleach消耗总量计算", "score": 0, "max_score": 30, "passed": False, "reason": f"期望 {gt['total_bleach_used']}, 实际 {a_used}. 请检查是否过滤了archive和.bak文件。"})
                
                # 4. 检查 total_bleach_lost_in_logs (30分)
                a_lost = agent_data.get("total_bleach_lost_in_logs")
                if a_lost == gt["total_bleach_lost_in_logs"]:
                    results["details"].append({"item": "Bleach流失量计算", "score": 30, "max_score": 30, "passed": True, "reason": "数值完全匹配"})
                else:
                    results["details"].append({"item": "Bleach流失量计算", "score": 0, "max_score": 30, "passed": False, "reason": f"期望 {gt['total_bleach_lost_in_logs']}, 实际 {a_lost}. 请检查对流失(N/A/None)的判定。"})

                # 5. 检查 inventory_discrepancy (20分)
                a_disc = agent_data.get("inventory_discrepancy")
                if a_disc == gt["inventory_discrepancy"]:
                    results["details"].append({"item": "库存差异对账计算", "score": 20, "max_score": 20, "passed": True, "reason": "数值完全匹配"})
                else:
                    results["details"].append({"item": "库存差异对账计算", "score": 0, "max_score": 20, "passed": False, "reason": f"期望 {gt['inventory_discrepancy']}, 实际 {a_disc}. 请检查公式: LogUsed - (Start - End)"})
            else:
                results["details"].append({"item": "环境基准检查", "score": 0, "max_score": 80, "passed": False, "reason": "无法读取原始日志生成对比基准"})

        except Exception as e:
            results["details"].append({"item": "数据内容检查", "score": 0, "max_score": 80, "passed": False, "reason": f"解析报错: {str(e)}"})

    # 计算总分
    results["total_score"] = sum(d["score"] for d in results["details"])
    with open(score_file, "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
