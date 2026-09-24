import os
import sys
import json
import csv
import re
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

def compute_ground_truth(workspace_root):
    # 1. Read registry mapping
    registry_path = os.path.join(workspace_root, "config", "device_registry.json")
    if not os.path.exists(registry_path):
        return {}
    with open(registry_path, "r", encoding="utf-8") as f:
        devices = json.load(f)
        
    # 2. Extract blackouts
    events_path = os.path.join(workspace_root, "sys_logs", "power_events.txt")
    blackouts = []
    if os.path.exists(events_path):
        with open(events_path, "r", encoding="utf-8") as f:
            content = f.read()
            matches = re.findall(r"between (\d+) and (\d+)", content)
            for m in matches:
                blackouts.append((int(m[0]), int(m[1])))
                
    # 3. Process data
    dumps_path = os.path.join(workspace_root, "sensor_dumps")
    expected_sums = {}
    expected_counts = {}
    
    if not os.path.exists(dumps_path):
        return {}
        
    for root_dir, _, files in os.walk(dumps_path):
        for file in files:
            file_path = os.path.join(root_dir, file)
            # Process CSV
            if file.endswith(".csv"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row.get("device_id") and row.get("timestamp") and row.get("amplitude") and row.get("status"):
                                dev_id = row["device_id"]
                                try:
                                    ts = int(row["timestamp"])
                                    amp = float(row["amplitude"])
                                except ValueError:
                                    continue
                                status = row["status"]
                                
                                is_blackout = any(start <= ts <= end for start, end in blackouts)
                                if not is_blackout and amp >= 0 and status == "OK" and dev_id in devices:
                                    samp_id = devices[dev_id]
                                    expected_sums[samp_id] = expected_sums.get(samp_id, 0.0) + amp
                                    expected_counts[samp_id] = expected_counts.get(samp_id, 0) + 1
                except Exception:
                    pass
            # Process JSONL
            elif file.endswith(".jsonl"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if not line.strip(): continue
                            data = json.loads(line)
                            dev_id = data.get("device_id")
                            try:
                                ts = int(data.get("timestamp", 0))
                                amp = float(data.get("amplitude", -1))
                            except ValueError:
                                continue
                            status = data.get("status")
                            
                            is_blackout = any(start <= ts <= end for start, end in blackouts)
                            if not is_blackout and amp >= 0 and status == "OK" and dev_id in devices:
                                samp_id = devices[dev_id]
                                expected_sums[samp_id] = expected_sums.get(samp_id, 0.0) + amp
                                expected_counts[samp_id] = expected_counts.get(samp_id, 0) + 1
                except Exception:
                    pass
                    
    # Calculate averages
    expected_averages = {s: round(expected_sums[s] / expected_counts[s], 2) 
                         for s in expected_counts if expected_counts[s] > 0}
    return expected_averages

def verify_workplace(workspace):
    details = []
    total_score = 0
    
    target_file = os.path.join(workspace, "workspace", "clean_metrics.json")
    
    # 1. Check if file exists and is valid JSON
    if not os.path.exists(target_file):
        details.append({"item": "检查结果文件 clean_metrics.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2, ensure_ascii=False)
        return

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            agent_data = json.load(f)
        details.append({"item": "检查结果文件 clean_metrics.json 是否存在且为有效 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且格式合法"})
        total_score += 10
    except json.JSONDecodeError:
        details.append({"item": "检查结果文件 clean_metrics.json 是否存在且为有效 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件无法解析为 JSON"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 2. Check for Hallucinations / Strict Schema
    ground_truth = compute_ground_truth(workspace)
    valid_samples = set(ground_truth.keys())
    agent_samples = set(agent_data.keys())
    
    if len(agent_samples) > 0 and agent_samples.issubset(valid_samples):
        details.append({"item": "检查是否未捏造多余样本或格式化异常", "score": 20, "max_score": 20, "passed": True, "reason": "Schema 合法，无未注册的数据键值"})
        total_score += 20
    else:
        extra = agent_samples - valid_samples
        details.append({"item": "检查是否未捏造多余样本或格式化异常", "score": 0, "max_score": 20, "passed": False, "reason": f"Agent 数据包含了未知的或捏造的字段: {extra}"})

    # 3. Precision verification of computed metrics
    if not ground_truth:
        details.append({"item": "计算探针自身的 Ground Truth 失败", "score": 0, "max_score": 70, "passed": False, "reason": "环境未生成有效的测试数据"})
    else:
        score_per_sample = 70.0 / len(ground_truth)
        math_score = 0
        for s_id, expected_val in ground_truth.items():
            if s_id in agent_data:
                try:
                    agent_val = float(agent_data[s_id])
                    if abs(agent_val - expected_val) <= 0.01:
                        math_score += score_per_sample
                        details.append({"item": f"检查样本 {s_id} 的计算结果", "score": round(score_per_sample), "max_score": round(score_per_sample), "passed": True, "reason": f"结果 {agent_val} 与 Ground Truth ({expected_val}) 一致"})
                    else:
                        details.append({"item": f"检查样本 {s_id} 的计算结果", "score": 0, "max_score": round(score_per_sample), "passed": False, "reason": f"预期为 {expected_val}，实际给出 {agent_val} (可能未正确执行状态过滤或处理停电黑名单)"})
                except (ValueError, TypeError):
                    details.append({"item": f"检查样本 {s_id} 的计算结果", "score": 0, "max_score": round(score_per_sample), "passed": False, "reason": f"值不可转换为浮点数: {agent_data[s_id]}"})
            else:
                details.append({"item": f"检查样本 {s_id} 的计算结果", "score": 0, "max_score": round(score_per_sample), "passed": False, "reason": f"缺失该样本数据的统计"})
        
        total_score += int(round(math_score))

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": min(total_score, 100), "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace_dir)
