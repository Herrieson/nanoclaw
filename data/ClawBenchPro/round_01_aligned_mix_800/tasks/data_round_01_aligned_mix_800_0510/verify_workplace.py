import os
import sys
import json
import csv
import math
import httpx
from openai import OpenAI

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

def generate_ground_truth(raw_dir):
    rates = {
        "EUR": 1.10, "GBP": 1.25, "JPY": 0.007,
        "AUD": 0.65, "CAD": 0.75, "USD": 1.0
    }
    dead_statuses = {'permanently_closed', 'bankrupt', 'sold'}
    
    branches = {}
    registry_dir = os.path.join(raw_dir, "branch_registry")
    if os.path.exists(registry_dir):
        for fname in os.listdir(registry_dir):
            if fname.endswith(".json"):
                with open(os.path.join(registry_dir, fname), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    b_id = data.get("branch_id")
                    if b_id:
                        branches[b_id] = {
                            "status": data.get("status"),
                            "currency": data.get("currency_code"),
                            "region": data.get("region"),
                            "is_alive": data.get("status") not in dead_statuses
                        }
                    
    q1_data = {}
    q1_dir = os.path.join(raw_dir, "q1_reports")
    if os.path.exists(q1_dir):
        for fname in os.listdir(q1_dir):
            if fname.endswith("_final.csv"):
                with open(os.path.join(q1_dir, fname), "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get("fiscal_year") == "2023":
                            q1_data[row["branch_id"]] = float(row.get("local_profit_q1", 0))
                            
    q2_data = {}
    q2_dir = os.path.join(raw_dir, "q2_reports")
    if os.path.exists(q2_dir):
        for fname in os.listdir(q2_dir):
            if fname.endswith(".json"):
                with open(os.path.join(q2_dir, fname), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for row in data.get("data", []):
                        if str(row.get("year")) == "2023":
                            q2_data[row["branchId"]] = float(row.get("profit", 0))
                            
    expected = {}
    for b_id, info in branches.items():
        if info["is_alive"]:
            curr = info["currency"]
            rate = rates.get(curr, 1.0)
            q1 = q1_data.get(b_id, 0.0)
            q2 = q2_data.get(b_id, 0.0)
            q1_usd = q1 * rate
            q2_usd = q2 * rate
            q3_proj = ((q1_usd + q2_usd) / 2.0) * 1.05
            expected[b_id] = round(q3_proj, 2)
            
    return expected, branches

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    raw_dir = os.path.join(workspace, "raw_financials")
    target_file = os.path.join(workspace, "q3_forecast_summary.json")
    
    score_details = []
    total_score = 0
    
    # 1. 检查结果文件是否存在 (10 分)
    if not os.path.exists(target_file):
        score_details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 q3_forecast_summary.json 不存在"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2)
        return
    else:
        score_details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 q3_forecast_summary.json 存在"})
        total_score += 10
        
    # 2. 检查 JSON 格式与 Schema 合法性 (10 分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
            submission = json.loads(raw_content)
        if not isinstance(submission, dict):
            raise ValueError("Root element is not a dictionary.")
            
        is_schema_valid = all(isinstance(k, str) and isinstance(v, (int, float)) for k, v in submission.items())
        if is_schema_valid:
            score_details.append({"item": "检查 JSON Schema", "score": 10, "max_score": 10, "passed": True, "reason": "格式完全合法，是 branch_id 到数值的字典"})
            total_score += 10
        else:
            score_details.append({"item": "检查 JSON Schema", "score": 0, "max_score": 10, "passed": False, "reason": "格式错误：值必须全部为数字"})
            
    except Exception as e:
        score_details.append({"item": "检查 JSON Schema", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败：{e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 生成 Ground Truth
    expected_data, branches_info = generate_ground_truth(raw_dir)
    expected_keys = set(expected_data.keys())
    submitted_keys = set(submission.keys())

    # 3. 剔除死亡店铺验证 (25 分)
    dead_in_submission = []
    missing_alive = []
    
    for b_id in submitted_keys:
        if b_id in branches_info and not branches_info[b_id]["is_alive"]:
            dead_in_submission.append(b_id)
            
    for b_id in expected_keys:
        if b_id not in submitted_keys:
            missing_alive.append(b_id)
            
    survival_score = 25
    survival_reasons = []
    if dead_in_submission:
        survival_score -= min(15, len(dead_in_submission) * 2)
        survival_reasons.append(f"包含了 {len(dead_in_submission)} 家已阵亡店铺 (如 {dead_in_submission[0]})")
    if missing_alive:
        survival_score -= min(10, len(missing_alive) * 2)
        survival_reasons.append(f"遗漏了 {len(missing_alive)} 家存活店铺")
        
    if survival_score == 25:
        score_details.append({"item": "验证存活状态过滤规则", "score": 25, "max_score": 25, "passed": True, "reason": "完全正确地过滤了破产、关停或售出的店铺"})
    else:
        survival_score = max(0, survival_score)
        score_details.append({"item": "验证存活状态过滤规则", "score": survival_score, "max_score": 25, "passed": False, "reason": " | ".join(survival_reasons)})
    total_score += survival_score

    # 4. 幻觉与捏造验证 (15 分)
    fake_branches = [k for k in submitted_keys if k not in branches_info]
    if fake_branches:
        score_details.append({"item": "验证是否捏造未知节点", "score": 0, "max_score": 15, "passed": False, "reason": f"捏造了 {len(fake_branches)} 个不存在的 branch_id (如 {fake_branches[0]})"})
    else:
        score_details.append({"item": "验证是否捏造未知节点", "score": 15, "max_score": 15, "passed": True, "reason": "未发现捏造的 branch_id 节点"})
        total_score += 15

    # 5. 计算精度与正确性验证 (40 分)
    correct_count = 0
    common_keys = submitted_keys.intersection(expected_keys)
    
    for k in common_keys:
        # 允许 0.05 的舍入容差
        if math.isclose(submission[k], expected_data[k], abs_tol=0.05):
            correct_count += 1
            
    if len(expected_keys) > 0:
        accuracy_ratio = correct_count / len(expected_keys)
        calc_score = int(40 * accuracy_ratio)
    else:
        calc_score = 0
        
    if calc_score == 40:
        score_details.append({"item": "利润计算与汇率精度验证", "score": 40, "max_score": 40, "passed": True, "reason": "所有分店 Q3 预计利润计算完全准确，汇率与年份筛选正确"})
    else:
        score_details.append({"item": "利润计算与汇率精度验证", "score": calc_score, "max_score": 40, "passed": False, "reason": f"计算正确率 {accuracy_ratio*100:.1f}%，检查 2022 数据是否被混入，或是否使用了过期的历史汇率"})
    total_score += calc_score

    # 保存最终结果
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
