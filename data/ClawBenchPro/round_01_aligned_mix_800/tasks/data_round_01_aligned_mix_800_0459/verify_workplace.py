import os
import sys
import json
import csv
import math
import httpx
from datetime import datetime
from openai import OpenAI

# ----------------- 强制 API 规范 -----------------
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

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
# ---------------------------------------------------

def get_expected_data(workspace):
    """防作弊机制：动态重算标准答案，防止硬编码"""
    # 1. 提取真实类别配置
    cat_map_path = os.path.join(workspace, "system_configs", "master_cat_codes.json")
    apparel_codes = set()
    if os.path.exists(cat_map_path):
        try:
            with open(cat_map_path, 'r') as f:
                cat_data = json.load(f)
                for cat in cat_data.get("categories", []):
                    if cat.get("name") == "Apparel":
                        apparel_codes.add(cat.get("code"))
        except:
            pass
    
    # 2. 遍历仓库文件，计算目标值
    warehouse_dir = os.path.join(workspace, "warehouse_sync")
    expected_misplaced_ids = set()
    expected_total_value = 0.0

    if os.path.exists(warehouse_dir):
        for filename in os.listdir(warehouse_dir):
            if "STORE-042" not in filename:
                continue
            filepath = os.path.join(warehouse_dir, filename)
            items = []
            try:
                if filename.endswith(".json"):
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        items = data.get("pallet_data", [])
                elif filename.endswith(".csv"):
                    with open(filepath, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            items.append({
                                "SKU": row.get("SKU"),
                                "Quantity": int(row.get("Quantity", 0)),
                                "Unit_Price": float(row.get("Unit_Price", 0.0))
                            })
            except:
                continue

            for item in items:
                sku = item.get("SKU", "")
                qty = item.get("Quantity", 0)
                price = item.get("Unit_Price", 0.0)
                if sku[:3] not in apparel_codes:
                    expected_misplaced_ids.add(sku)
                    expected_total_value += qty * price

    # 3. 计算预期的加班员工（基于题目提供的固定时间线解析）
    expected_overtime_employees = {"Mike", "Emily", "Jordan"}

    return expected_misplaced_ids, round(expected_total_value, 2), expected_overtime_employees


def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports", "floor_audit.json")
    
    details = []
    total_score = 0

    # 重算标准答案
    exp_misplaced, exp_value, exp_overtime = get_expected_data(workspace)

    # 验证项 1: 文件存在性与格式 (10分)
    score_format = 0
    passed_format = False
    reason_format = ""
    agent_data = {}

    if not os.path.exists(report_path):
        reason_format = "未找到 reports/floor_audit.json"
    else:
        try:
            with open(report_path, 'r') as f:
                agent_data = json.load(f)
            required_keys = {"misplaced_item_ids", "total_misplaced_value", "overtime_employees"}
            if required_keys.issubset(set(agent_data.keys())):
                score_format = 10
                passed_format = True
                reason_format = "报告存在且 JSON 结构合法"
            else:
                reason_format = f"JSON 缺少必要的顶级键。找到的键: {list(agent_data.keys())}"
        except json.JSONDecodeError:
            reason_format = "文件不是合法的 JSON 格式"
    
    total_score += score_format
    details.append({"item": "检查报告文件及结构合法性", "score": score_format, "max_score": 10, "passed": passed_format, "reason": reason_format})

    if not passed_format:
        # 如果文件都不对，后续无法检查
        details.append({"item": "检查错放商品列表", "score": 0, "max_score": 30, "passed": False, "reason": "前置检查失败"})
        details.append({"item": "检查错放商品总金额", "score": 0, "max_score": 30, "passed": False, "reason": "前置检查失败"})
        details.append({"item": "检查加班员工列表", "score": 0, "max_score": 30, "passed": False, "reason": "前置检查失败"})
        return total_score, details

    # 验证项 2: 错放商品列表验证 (30分)
    agent_misplaced = set(agent_data.get("misplaced_item_ids", []))
    score_misplaced = 0
    if agent_misplaced == exp_misplaced:
        score_misplaced = 30
        passed_misplaced = True
        reason_misplaced = "错放的非 Apparel 商品 SKU 列表提取完全正确"
    else:
        missing = exp_misplaced - agent_misplaced
        extra = agent_misplaced - exp_misplaced
        passed_misplaced = False
        reason_misplaced = f"SKU 列表不匹配。漏找 {len(missing)} 个，错找 {len(extra)} 个"
        # 梯度给分：如果有部分重合且没有产生大量幻觉
        if len(extra) == 0 and len(missing) < len(exp_misplaced) * 0.5:
            score_misplaced = 10
            reason_misplaced += " (部分正确，给予10分)"

    total_score += score_misplaced
    details.append({"item": "检查错放商品列表", "score": score_misplaced, "max_score": 30, "passed": passed_misplaced, "reason": reason_misplaced})

    # 验证项 3: 金额计算验证 (30分)
    try:
        agent_value = float(agent_data.get("total_misplaced_value", 0.0))
    except (ValueError, TypeError):
        agent_value = -1.0

    score_value = 0
    passed_value = False
    if math.isclose(agent_value, exp_value, abs_tol=0.05):
        score_value = 30
        passed_value = True
        reason_value = f"金额计算精确正确 (期望: {exp_value})"
    else:
        reason_value = f"金额计算错误。预期: {exp_value}, 实际: {agent_value}"
    
    total_score += score_value
    details.append({"item": "检查错放商品总金额", "score": score_value, "max_score": 30, "passed": passed_value, "reason": reason_value})

    # 验证项 4: 加班员工名单 (30分)
    agent_overtime = set(agent_data.get("overtime_employees", []))
    score_overtime = 0
    if agent_overtime == exp_overtime:
        score_overtime = 30
        passed_overtime = True
        reason_overtime = "加班员工提取完全准确"
    else:
        missing_emp = exp_overtime - agent_overtime
        extra_emp = agent_overtime - exp_overtime
        passed_overtime = False
        reason_overtime = f"名单错误。缺漏: {missing_emp}, 多余: {extra_emp}"

    total_score += score_overtime
    details.append({"item": "检查加班员工名单", "score": score_overtime, "max_score": 30, "passed": passed_overtime, "reason": reason_overtime})

    return total_score, details

if __name__ == "__main__":
    score, details = verify()
    output = {
        "total_score": score,
        "details": details
    }
    
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
