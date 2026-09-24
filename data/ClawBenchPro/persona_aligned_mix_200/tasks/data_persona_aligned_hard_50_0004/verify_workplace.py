import os
import sys
import json
import httpx
import re
import glob
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

def compute_ground_truth(workspace):
    # Initial logic and parameters are validated
    try:
        with open(os.path.join(workspace, "sys_config/safety_params.json"), "r") as f:
            safety_params = json.load(f)
            highway_params = safety_params["profiles"]["highway"]
            min_conf = highway_params["min_confidence"]
            max_drift = highway_params["max_time_drift_ms"]
            
        with open(os.path.join(workspace, "sys_config/dbc_mapping.txt"), "r") as f:
            dbc_content = f.read()
            match = re.search(r"FRONT_RADAR_OBJ=0x([0-9A-Fa-f]+)", dbc_content)
            radar_id = match.group(1).upper() if match else "1B3"
            
        can_data = {}
        for log_file in glob.glob(os.path.join(workspace, "vehicle_logs/can_bus/trace_part_*.log")):
            with open(log_file, "r") as f:
                for line in f:
                    if f" {radar_id} " in line:
                        parts = line.split("] can1 RX - -")
                        ts = float(parts[0].strip("["))
                        payload = parts[1].split("[8]")[1].strip().split()
                        obj_id = int(payload[0], 16)
                        can_data[obj_id] = ts

        vision_data = {}
        for json_file in glob.glob(os.path.join(workspace, "vehicle_logs/vision_frames/camera_front/*.json")):
            with open(json_file, "r") as f:
                data = json.load(f)
                meta = data.get("metadata", {})
                if meta.get("frame_status") == "VALID" and meta.get("sensor") == "front_center_camera":
                    ts_ms = data["frame_info"]["system_timestamp_ms"]
                    for entity in data.get("detected_entities", []):
                        obj_id = entity["entity_id"]
                        conf = entity["metrics"]["confidence_score"]
                        vision_data[obj_id] = {"ts_ms": ts_ms, "conf": conf}

        ghost_ids = []
        for obj_id in can_data.keys():
            if obj_id in vision_data:
                can_ts_ms = can_data[obj_id] * 1000
                vis_ts_ms = vision_data[obj_id]["ts_ms"]
                conf = vision_data[obj_id]["conf"]
                drift = abs(can_ts_ms - vis_ts_ms)
                
                if conf < min_conf or drift > max_drift:
                    ghost_ids.append(obj_id)
                    
        return sorted(ghost_ids)
    except Exception as e:
        return []

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    
    target_file = os.path.join(workspace, "calibration/ghost_ids.txt")
    file_exists = os.path.exists(target_file)
    
    details.append({
        "item": "检查目标文件是否创建",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "找到 calibration/ghost_ids.txt" if file_exists else "未找到 calibration/ghost_ids.txt"
    })
    
    if file_exists:
        try:
            with open(target_file, "r") as f:
                content = f.read().strip()
            
            agent_ids = [int(x.strip()) for x in content.split(",") if x.strip().isdigit()]
            is_sorted = agent_ids == sorted(agent_ids)
            format_passed = len(agent_ids) > 0 and is_sorted
            
            details.append({
                "item": "检查文件格式合法性及升序排列",
                "score": 10 if format_passed else 0,
                "max_score": 10,
                "passed": format_passed,
                "reason": "逗号分隔的十进制 ID 且升序" if format_passed else "格式非法或未升序"
            })
            
            ground_truth = compute_ground_truth(workspace)
            gt_set = set(ground_truth)
            ag_set = set(agent_ids)
            
            correct_ids = gt_set.intersection(ag_set)
            false_positives = ag_set - gt_set
            false_negatives = gt_set - ag_set
            
            # Direct Final Transformation evaluation
            precision_score = max(0, 40 - len(false_positives) * 10)
            recall_score = max(0, 40 - len(false_negatives) * 10)
            
            calc_score = 0
            if format_passed and len(gt_set) > 0:
                if len(false_positives) == 0 and len(false_negatives) == 0:
                    calc_score = 80
                else:
                    calc_score = precision_score + recall_score
                    
            details.append({
                "item": "检查幽灵障碍物计算精确度 (拒绝幻觉与遗漏)",
                "score": calc_score,
                "max_score": 80,
                "passed": calc_score == 80,
                "reason": f"命中:{len(correct_ids)}/GT:{len(gt_set)}, 误报:{len(false_positives)}, 漏报:{len(false_negatives)}"
            })
            
        except Exception as e:
            details.append({
                "item": "检查文件格式合法性及升序排列",
                "score": 0, "max_score": 10, "passed": False, "reason": "解析异常"
            })
            details.append({
                "item": "检查幽灵障碍物计算精确度 (拒绝幻觉与遗漏)",
                "score": 0, "max_score": 80, "passed": False, "reason": "无法进行数据比对"
            })
    else:
        details.append({"item": "检查文件格式合法性及升序排列", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        details.append({"item": "检查幽灵障碍物计算精确度 (拒绝幻觉与遗漏)", "score": 0, "max_score": 80, "passed": False, "reason": "文件缺失"})

    total_score = sum(d["score"] for d in details)
    
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
