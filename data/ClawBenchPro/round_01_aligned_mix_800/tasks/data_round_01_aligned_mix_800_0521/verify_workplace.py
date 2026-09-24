import os
import sys
import json
import csv
import glob
import re
from pathlib import Path

def calculate_ground_truth(workspace):
    """
    根据 env_builder.py 的逻辑，在评测脚本中重新计算一份 Ground Truth。
    这确保了无论随机生成的结果是什么，验证脚本都能得到准确的预期值。
    """
    # 1. 解析 Catalog 获取目标产品 ID 和 价格
    catalog_path = os.path.join(workspace, "records/catalog.json")
    if not os.path.exists(catalog_path):
        return None, None, None
    
    with open(catalog_path, 'r') as f:
        catalog = json.load(f)
    
    target_prod_name = "Smart Soil Monitor"
    target_prod_id = None
    target_price = 0.0
    
    for cat in catalog['data']['inventory']['categories']:
        for item in cat['items']:
            if item['desc'] == target_prod_name:
                target_prod_id = item['id']
                target_price = float(item['retail_price'].replace('$', '').strip())
                break
    
    # 2. 扫描客户，获取真实客户及其邮箱/属性
    real_customer_ids = set()
    wellness_emails = set()
    keywords = ["health", "wellness", "garden"]
    
    customer_files = glob.glob(os.path.join(workspace, "records/customers/*/*.json"))
    for cf in customer_files:
        with open(cf, 'r') as f:
            c = json.load(f)
            if not c.get('is_test', False):
                real_customer_ids.add(c['customer_id'])
                note = c.get('profile_note', "").lower()
                if any(kw in note for kw in keywords):
                    wellness_emails.add(c['email'])
    
    # 3. 计算收入
    total_revenue = 0.0
    order_files = glob.glob(os.path.join(workspace, "records/orders/*.csv"))
    for of in order_files:
        with open(of, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 过滤条件：产品匹配、状态 completed、非测试客户
                if (row['prod_id'] == target_prod_id and 
                    row['status'] == 'completed' and 
                    row['cust_id'] in real_customer_ids):
                    qty = int(row['quantity'].strip())
                    total_revenue += qty * target_price
                    
    return wellness_emails, total_revenue, target_prod_id

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    score_file = os.path.join(workspace, "workplace_score.json")
    
    details = []
    total_score = 0
    
    # 获取标准答案
    true_emails, true_revenue, target_id = calculate_ground_truth(workspace)
    if true_emails is None:
        details.append({"item": "基础环境检查", "score": 0, "max_score": 100, "passed": False, "reason": "未找到原始记录文件，环境构建可能失败"})
        with open(score_file, 'w') as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # --- 任务 1: wellness_leads.txt 验证 (40分) ---
    leads_path = os.path.join(deliverables_dir, "wellness_leads.txt")
    if os.path.exists(leads_path):
        with open(leads_path, 'r') as f:
            agent_emails = set(line.strip() for line in f if line.strip())
        
        # 检查是否包含测试账号 (一票否决)
        test_in_list = any("test_" in e or "internal.dev" in e for e in agent_emails)
        
        if test_in_list:
            details.append({"item": "Leads列表过滤测试账号", "score": 0, "max_score": 20, "passed": False, "reason": "列表中包含测试账号或内网开发邮箱"})
        else:
            # 检查准确率和召回率
            intersection = agent_emails.intersection(true_emails)
            if len(true_emails) > 0:
                recall = len(intersection) / len(true_emails)
                precision = len(intersection) / len(agent_emails) if len(agent_emails) > 0 else 0
                
                if recall > 0.95 and precision > 0.95:
                    s = 40
                    res = "完全匹配"
                elif recall > 0.8:
                    s = 20
                    res = "大部分匹配，但存在少量遗漏或多余"
                else:
                    s = 5
                    res = f"匹配度较低 (Recall: {recall:.2f})"
                details.append({"item": "Leads列表内容准确性", "score": s, "max_score": 40, "passed": s > 20, "reason": res})
                total_score += s
            else:
                details.append({"item": "Leads列表内容准确性", "score": 40, "max_score": 40, "passed": True, "reason": "标准答案集为空且Agent未生成额外内容"})
                total_score += 40
    else:
        details.append({"item": "检查 wellness_leads.txt 是否生成", "score": 0, "max_score": 40, "passed": False, "reason": "文件缺失"})

    # --- 任务 2: soil_monitor_revenue.txt 验证 (60分) ---
    rev_path = os.path.join(deliverables_dir, "soil_monitor_revenue.txt")
    if os.path.exists(rev_path):
        try:
            with open(rev_path, 'r') as f:
                content = f.read().strip()
                # 尝试提取第一个数字
                match = re.search(r"(\d+\.?\d*)", content)
                agent_revenue = float(match.group(1)) if match else -1.0
            
            diff = abs(agent_revenue - true_revenue)
            if diff < 0.01:
                s = 60
                res = f"金额完全正确: {true_revenue}"
            elif diff < (true_revenue * 0.05):
                s = 30
                res = f"金额接近但有小额误差。预期: {true_revenue}, 得到: {agent_revenue}。可能是未处理空格、清洗数据不全或过滤条件有微小偏差。"
            else:
                s = 0
                res = f"金额错误。预期: {true_revenue}, 实际提取到: {agent_revenue}。极大概率是没过滤 test_account 或 status != completed。"
            
            details.append({"item": "Smart Soil Monitor 营收计算", "score": s, "max_score": 60, "passed": s == 60, "reason": res})
            total_score += s
        except Exception as e:
            details.append({"item": "Smart Soil Monitor 营收计算", "score": 0, "max_score": 60, "passed": False, "reason": f"解析文件内容失败: {str(e)}"})
    else:
        details.append({"item": "检查 soil_monitor_revenue.txt 是否生成", "score": 0, "max_score": 60, "passed": False, "reason": "文件缺失"})

    # 最终分档
    with open(score_file, 'w') as f:
        json.dump({"total_score": int(total_score), "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
