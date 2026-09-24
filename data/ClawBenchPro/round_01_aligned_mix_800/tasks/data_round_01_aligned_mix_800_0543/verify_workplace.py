import os
import sys
import json
import re
import math
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    # 此函数为检测非结构化文本的统一接口
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

def get_ground_truth(workspace):
    policy_file = os.path.join(workspace, "hospital_records", "clearance_policy.json")
    with open(policy_file, "r") as f:
        policy = json.load(f)
    min_gain, max_gain = policy["medical_constraints"]["elevation_gain_range_m"]
    max_steepness_limit = policy["medical_constraints"]["max_steepness_m_per_km"]

    active_file = os.path.join(workspace, "forestry_dept", "active_trails_q3.txt")
    active_trails = set()
    with open(active_file, "r") as f:
        for line in f:
            match = re.search(r'(trail_\d{3})', line)
            if match:
                active_trails.add(match.group(1))

    telemetry_dir = os.path.join(workspace, "telemetry_dumps")
    optimal = {}
    
    for trail in active_trails:
        trail_dir = os.path.join(telemetry_dir, trail)
        if not os.path.exists(trail_dir):
            continue
        
        waypoints = []
        for file in os.listdir(trail_dir):
            if file.endswith(".json"):
                with open(os.path.join(trail_dir, file), "r") as f:
                    try:
                        wp = json.load(f)
                        waypoints.append(wp)
                    except:
                        pass
        
        try:
            # 必须按照 timestamp 排序
            waypoints.sort(key=lambda x: x["timestamp"])
        except KeyError:
            continue
            
        total_gain = 0.0
        max_steepness = 0.0
        is_valid = True
        
        for i in range(1, len(waypoints)):
            wp1 = waypoints[i-1]
            wp2 = waypoints[i]
            
            try:
                dist_change = float(wp2["distance_km"]) - float(wp1["distance_km"])
                elev_change = float(wp2["elevation_m"]) - float(wp1["elevation_m"])
            except:
                is_valid = False
                break
                
            if elev_change > 0:  # 严格忽略下降
                total_gain += elev_change
                if dist_change > 0:
                    steepness = elev_change / dist_change
                    if steepness > max_steepness:
                        max_steepness = steepness
                        
        if not is_valid:
            continue
            
        if min_gain <= total_gain <= max_gain and max_steepness <= max_steepness_limit:
            optimal[trail] = {
                "total_gain": round(total_gain, 2),
                "max_steepness": round(max_steepness, 2)
            }
            
    return optimal

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    # 1. 验证结果目录与文件是否存在 (10分)
    results_dir = os.path.join(workspace, "results")
    target_file = os.path.join(results_dir, "optimal_routes.json")
    
    if os.path.isdir(results_dir) and os.path.isfile(target_file):
        score_details.append({"item": "检查结果目录和文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功找到 results/optimal_routes.json"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录和文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 results 目录或 optimal_routes.json 文件"})
        # 严重错误，直接返回
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. 读取并验证 JSON 格式合法性 (15分)
    try:
        with open(target_file, "r") as f:
            agent_data = json.load(f)
        score_details.append({"item": "检查 JSON 解析合法性", "score": 15, "max_score": 15, "passed": True, "reason": "文件为合法 JSON"})
        total_score += 15
    except Exception as e:
        score_details.append({"item": "检查 JSON 解析合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"解析 JSON 失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 3. 计算 Ground Truth 进行比对
    gt_data = get_ground_truth(workspace)
    gt_keys = set(gt_data.keys())
    agent_keys = set(agent_data.keys())
    
    # 4. 验证轨迹匹配精准度 (35分)
    if gt_keys == agent_keys:
        score_details.append({"item": "验证筛选的路线集合是否完全正确", "score": 35, "max_score": 35, "passed": True, "reason": "识别出了完全正确的 trail 集合"})
        total_score += 35
    else:
        missing = gt_keys - agent_keys
        extra = agent_keys - gt_keys
        reason_str = ""
        if missing: reason_str += f"遗漏了有效路线 {missing}; "
        if extra: reason_str += f"包含了错误/幻觉路线 {extra}; "
        
        # 部分给分逻辑：如果没有捏造不存在的轨迹，且只找出了部分正确的，给少量分数
        if len(extra) > 0:
            score_details.append({"item": "验证筛选的路线集合是否完全正确", "score": 0, "max_score": 35, "passed": False, "reason": "包含错误路线，一票否决: " + reason_str})
        else:
            partial_score = int(35 * (len(agent_keys) / len(gt_keys)))
            score_details.append({"item": "验证筛选的路线集合是否完全正确", "score": partial_score, "max_score": 35, "passed": False, "reason": "部分正确: " + reason_str})
            total_score += partial_score

    # 5. 验证指标计算的精准度 (40分)
    math_correct_count = 0
    total_checks = len(agent_keys.intersection(gt_keys))
    if total_checks > 0:
        for k in agent_keys.intersection(gt_keys):
            try:
                a_gain = float(agent_data[k].get("total_gain", 0))
                a_steep = float(agent_data[k].get("max_steepness", 0))
                g_gain = gt_data[k]["total_gain"]
                g_steep = gt_data[k]["max_steepness"]
                
                # 容许 0.05 的舍入误差
                if abs(a_gain - g_gain) < 0.05 and abs(a_steep - g_steep) < 0.05:
                    math_correct_count += 1
            except:
                pass
                
        calc_score = int(40 * (math_correct_count / total_checks))
        if calc_score == 40:
            score_details.append({"item": "验证指标计算与保留两位小数的准确性", "score": 40, "max_score": 40, "passed": True, "reason": "地形指标计算完全正确"})
        else:
            score_details.append({"item": "验证指标计算与保留两位小数的准确性", "score": calc_score, "max_score": 40, "passed": False, "reason": f"有 {total_checks - math_correct_count} 个路线指标计算存在数值偏差或未正确解析 timestamp 导致错位"})
        total_score += calc_score
    else:
         score_details.append({"item": "验证指标计算与保留两位小数的准确性", "score": 0, "max_score": 40, "passed": False, "reason": "无正确匹配的路线进行指标比对"})

    # 写入文件
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
