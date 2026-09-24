import os
import sys
import json
import csv
import re

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception:
        return ""

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查结果文件是否存在 (10 points)
    damaged_report_path = os.path.join(workspace, "damaged_report.json")
    restock_summary_path = os.path.join(workspace, "restock_summary.txt")
    
    damaged_exists = os.path.exists(damaged_report_path)
    restock_exists = os.path.exists(restock_summary_path)
    
    if damaged_exists:
        score += 5
        details.append({"item": "文件存在: damaged_report.json", "score": 5, "max_score": 5, "passed": True})
    else:
        details.append({"item": "文件存在: damaged_report.json", "score": 0, "max_score": 5, "passed": False})

    if restock_exists:
        score += 5
        details.append({"item": "文件存在: restock_summary.txt", "score": 5, "max_score": 5, "passed": True})
    else:
        details.append({"item": "文件存在: restock_summary.txt", "score": 0, "max_score": 5, "passed": False})

    # 重新计算正确答案以进行对比 (由 env_builder 逻辑得出)
    # 此处逻辑应与 env_builder.py 严丝合缝
    vault_root = os.path.join(workspace, "vault_dump")
    ground_truth_damaged_skus = []
    ground_truth_restock_total = 0

    if os.path.exists(vault_root):
        for root, dirs, files in os.walk(vault_root):
            # 过滤噪音
            if "temp_session" in root or "archive_2022" in root:
                continue
            
            for file in files:
                if "_bak" in file or "_tmp" in file or "calibration" in file:
                    continue
                
                path = os.path.join(root, file)
                # 处理 JSON shards
                if file.endswith(".json") and "shards" in root:
                    data = load_json(path)
                    if data:
                        sku = data["item_id"]
                        status = data["meta"]["state"]
                        cur = data["meta"]["counts"]["on_hand"]
                        req = data["meta"]["counts"]["required"]
                        if status in ["damaged", "broken"]:
                            ground_truth_damaged_skus.append(sku)
                        if cur < req:
                            ground_truth_restock_total += (req - cur)
                
                # 处理 CSV
                elif file == "manifest.csv":
                    with open(path, 'r') as f:
                        reader = csv.reader(f)
                        next(reader) # skip header
                        for row in reader:
                            if len(row) < 5: continue
                            sku, status, cur, req = row[0], row[2], int(row[3]), int(row[4])
                            if status in ["damaged", "broken"]:
                                ground_truth_damaged_skus.append(sku)
                            if cur < req:
                                ground_truth_restock_total += (req - cur)

                # 处理 Log
                elif file == "stream.log":
                    content = read_file(path)
                    for line in content.split("\n"):
                        if not line.startswith("ENTRY|"): continue
                        parts = line.split("|")
                        if len(parts) < 6: continue
                        sku, status, cur, req = parts[1], parts[3], int(parts[4]), int(parts[5])
                        if status in ["damaged", "broken"]:
                            ground_truth_damaged_skus.append(sku)
                        if cur < req:
                            ground_truth_restock_total += (req - cur)

    # 2. 验证 damaged_report.json 内容 (40 points)
    if damaged_exists:
        agent_damaged = load_json(damaged_report_path)
        if isinstance(agent_damaged, list):
            agent_skus = [str(item.get("SKU") or item.get("sku", "")) for item in agent_damaged]
            
            # 检查是否包含测试数据 (Red Herring)
            has_test_data = any("TEST-999" in s or "OLD-1" in s for s in agent_skus)
            
            # 集合比对
            set_gt = set(ground_truth_damaged_skus)
            set_ag = set(agent_skus)
            
            intersection = set_gt.intersection(set_ag)
            recall = len(intersection) / len(set_gt) if set_gt else 1
            precision = len(intersection) / len(set_ag) if set_ag else 1
            
            if has_test_data:
                details.append({"item": "损坏报告: 错误包含系统测试/旧数据", "score": 0, "max_score": 10, "passed": False})
            else:
                score += 10
                details.append({"item": "损坏报告: 成功过滤噪音数据", "score": 10, "max_score": 10, "passed": True})

            report_score = int(30 * (recall * 0.7 + precision * 0.3))
            score += report_score
            details.append({"item": "损坏报告: 数据准确率与召回率", "score": report_score, "max_score": 30, "passed": recall > 0.9})
        else:
            details.append({"item": "损坏报告: 格式非JSON数组", "score": 0, "max_score": 40, "passed": False})
    else:
        details.append({"item": "损坏报告: 未生成", "score": 0, "max_score": 40, "passed": False})

    # 3. 验证 restock_summary.txt 内容 (50 points)
    if restock_exists:
        try:
            content = read_file(restock_summary_path)
            # 提取数字
            numbers = re.findall(r'\d+', content)
            if numbers:
                agent_total = int(numbers[0])
                if agent_total == ground_truth_restock_total:
                    score += 50
                    details.append({"item": "补货总数: 数值完全正确", "score": 50, "max_score": 50, "passed": True, "reason": f"结果为 {agent_total}"})
                elif abs(agent_total - ground_truth_restock_total) < (ground_truth_restock_total * 0.05):
                    score += 25
                    details.append({"item": "补货总数: 数值接近 (偏差<5%)", "score": 25, "max_score": 50, "passed": False, "reason": f"期望 {ground_truth_restock_total}, 实际 {agent_total}"})
                else:
                    details.append({"item": "补货总数: 数值错误", "score": 0, "max_score": 50, "passed": False, "reason": f"期望 {ground_truth_restock_total}, 实际 {agent_total}"})
            else:
                details.append({"item": "补货总数: 未能在文件中找到有效数字", "score": 0, "max_score": 50, "passed": False})
        except:
            details.append({"item": "补货总数: 文件读取解析失败", "score": 0, "max_score": 50, "passed": False})
    else:
        details.append({"item": "补货总数: 未生成", "score": 0, "max_score": 50, "passed": False})

    # 输出结果
    output = {"total_score": min(100, score), "details": details}
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
