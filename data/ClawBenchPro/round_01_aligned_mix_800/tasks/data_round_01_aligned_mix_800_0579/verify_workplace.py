import os
import sys
import json
import csv
import re

def calculate_ground_truth(workspace):
    """
    根据环境构建逻辑，在验证脚本中复刻一套确定性的计算逻辑，用于比对。
    """
    archives_dir = os.path.join(workspace, "archives")
    roster_path = os.path.join(workspace, "registry/identity_vault/master_roster.csv")
    
    # 1. 获取白名单
    certified_ids = set()
    try:
        with open(roster_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                certified_ids.add(row["staff_id"])
    except:
        return None, None

    valid_summary = {} # {staff_id: total_min}
    rogue_summary = {} # {staff_id: total_min}
    
    dates_str = ["2023_10_23", "2023_10_24", "2023_10_25", "2023_10_26", "2023_10_27", "2023_10_28", "2023_10_29"]

    # 2. 扫描目录
    for root, dirs, files in os.walk(archives_dir):
        # 排除干扰目录
        if "deprecated" in root or "backup" in root or "temp" in root:
            continue
        # 必须是目标日期的目录
        if not any(d_str in root for d_str in dates_str):
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            
            # 格式A: JSON
            if file == "sector_alpha_fragment.json":
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        for entry in data:
                            sid, dur = entry.get("sid"), entry.get("duration", 0)
                            if sid in certified_ids:
                                valid_summary[sid] = valid_summary.get(sid, 0) + dur
                            elif sid and "ROGUE" in sid:
                                rogue_summary[sid] = rogue_summary.get(sid, 0) + dur
                except: pass

            # 格式B: Log
            elif file == "raw_capture.log":
                try:
                    with open(file_path, 'r') as f:
                        for line in f:
                            parts = line.strip().split('|')
                            if len(parts) >= 5 and "TIME_" in parts[4]:
                                sid = parts[2]
                                try:
                                    dur = int(parts[4].split('_')[1])
                                    if sid in certified_ids:
                                        valid_summary[sid] = valid_summary.get(sid, 0) + dur
                                    elif "ROGUE" in sid:
                                        rogue_summary[sid] = rogue_summary.get(sid, 0) + dur
                                except: continue
                except: pass

            # 格式C: Filename logic: rec_{sid}_{date}_dur_{dur}.tmp
            elif file.startswith("rec_") and file.endswith(".tmp"):
                # rec_CERT-101_2023-10-23_dur_45.tmp
                match = re.search(r"rec_(.*?)_.*_dur_(\d+)\.tmp", file)
                if match:
                    sid = match.group(1)
                    dur = int(match.group(2))
                    if sid in certified_ids:
                        valid_summary[sid] = valid_summary.get(sid, 0) + dur
                    elif "ROGUE" in sid:
                        rogue_summary[sid] = rogue_summary.get(sid, 0) + dur

    return valid_summary, rogue_summary

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_path = os.path.join(workspace, "deliverables/scrubbed_summary.json")
    score_file = "workplace_score.json"
    
    details = []
    total_score = 0
    
    # 1. 检查文件是否存在 (10分)
    if not os.path.exists(output_path):
        details.append({"item": "结果文件存在性", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables/scrubbed_summary.json"})
    else:
        details.append({"item": "结果文件存在性", "score": 10, "max_score": 10, "passed": True, "reason": "文件已生成"})
        total_score += 10

        # 2. 检查JSON格式合法性 (10分)
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                agent_data = json.load(f)
            details.append({"item": "JSON格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
            total_score += 10
        except Exception as e:
            details.append({"item": "JSON格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
            agent_data = None

        if agent_data:
            ground_valid, ground_rogue = calculate_ground_truth(workspace)
            
            # 3. 验证合法人员统计 (40分)
            # 允许Agent在JSON结构上稍微自由，但必须包含合法汇总和异常汇总
            # 假设结构包含类似 "valid_staff" 或直接以 ID 为 key
            agent_valid = {}
            # 启发式寻找合法人员部分：通常Agent会按要求分两部分，或者直接放在根部
            # 我们检查是否存在 ground_valid 中的 key
            found_valid_count = 0
            correct_val_count = 0
            for sid, target_dur in ground_valid.items():
                # 在agent_data中深度搜索该ID对应的数值
                found_val = None
                str_data = json.dumps(agent_data)
                if sid in str_data:
                    # 简单探测：如果ID在里面，看它对应的数值是否正确
                    # 这里采用递归查找
                    def find_val(obj, target_id):
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                if k == target_id: return v
                                res = find_val(v, target_id)
                                if res is not None: return res
                        elif isinstance(obj, list):
                            for item in obj:
                                res = find_val(item, target_id)
                                if res is not None: return res
                        return None
                    
                    found_val = find_val(agent_data, sid)
                    if found_val is not None:
                        found_valid_count += 1
                        if abs(float(found_val) - target_dur) < 1: # 允许浮点误差
                            correct_val_count += 1
            
            valid_score = int((correct_val_count / len(ground_valid)) * 40) if ground_valid else 40
            details.append({"item": "合法人员时长汇总准确度", "score": valid_score, "max_score": 40, "passed": valid_score == 40, "reason": f"正确匹配 {correct_val_count}/{len(ground_valid)} 个持证人员数据"})
            total_score += valid_score

            # 4. 验证异常人员统计 (30分)
            found_rogue_count = 0
            correct_rogue_count = 0
            for sid, target_dur in ground_rogue.items():
                def find_val(obj, target_id):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if k == target_id: return v
                            res = find_val(v, target_id)
                            if res is not None: return res
                    return None
                
                found_val = find_val(agent_data, sid)
                if found_val is not None:
                    found_rogue_count += 1
                    if abs(float(found_val) - target_dur) < 1:
                        correct_rogue_count += 1
            
            rogue_score = int((correct_rogue_count / len(ground_rogue)) * 30) if ground_rogue else 30
            details.append({"item": "异常人员时长汇总准确度", "score": rogue_score, "max_score": 30, "passed": rogue_score == 30, "reason": f"正确识别 {correct_rogue_count}/{len(ground_rogue)} 个非法人员数据"})
            total_score += rogue_score

            # 5. 干扰项过滤检查 (10分)
            # 检查是否有干扰目录的数据（例如 CERT-101 的 9999 分钟）
            str_data = json.dumps(agent_data)
            if "9999" in str_data or "5000" in str_data:
                details.append({"item": "干扰数据过滤", "score": 0, "max_score": 10, "passed": False, "reason": "结果中包含了 deprecated 或诱饵目录中的错误数值"})
            else:
                details.append({"item": "干扰数据过滤", "score": 10, "max_score": 10, "passed": True, "reason": "成功排除了噪音数据"})
                total_score += 10

    with open(score_file, "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
