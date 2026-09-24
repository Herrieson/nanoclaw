import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    target_file = os.path.join(workspace, "calibration/ghost_ids.txt")
    
    # 1. 基础检查：文件是否存在 (10分)
    if os.path.exists(target_file):
        score += 10
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 ghost_ids.txt 存在"})
        
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            # 解析内容
            raw_ids = [s.strip() for s in content.split(",") if s.strip()]
            try:
                agent_ghost_ids = set(int(rid) for rid in raw_ids)
            except ValueError:
                details.append({"item": "检查文件内容格式", "score": 0, "max_score": 10, "passed": False, "reason": f"文件内容无法解析为整数列表: {content}"})
                return score, details

            # 2. 格式合规性检查 (10分)
            # 要求：仅逗号分隔，无额外描述
            if len(content.split("\n")) == 1 and "," in content:
                score += 10
                details.append({"item": "检查输出格式合规性", "score": 10, "max_score": 10, "passed": True, "reason": "格式符合逗号分隔要求"})
            else:
                details.append({"item": "检查输出格式合规性", "score": 0, "max_score": 10, "passed": False, "reason": "格式不符合单行逗号分隔要求"})

            # 3. 核心逻辑：检测幽灵障碍物 ID 的准确性
            # 根据 env_builder.py，正确答案是 {18, 27, 42, 68}
            # 正常 ID 是 {12, 33, 55}
            ground_truth_ghosts = {18, 27, 42, 68}
            ground_truth_normals = {12, 33, 55}
            
            # 正确识别的幽灵 (每个15分，共60分)
            for gid in ground_truth_ghosts:
                if gid in agent_ghost_ids:
                    score += 15
                    details.append({"item": f"检测幽灵 ID {gid}", "score": 15, "max_score": 15, "passed": True, "reason": "正确识别"})
                else:
                    details.append({"item": f"检测幽灵 ID {gid}", "score": 0, "max_score": 15, "passed": False, "reason": "漏检"})

            # 错误识别的正常障碍物 (误报，每个扣10分，最低到0分)
            for nid in ground_truth_normals:
                if nid in agent_ghost_ids:
                    score -= 10
                    details.append({"item": f"误报检查 ID {nid}", "score": -10, "max_score": 0, "passed": False, "reason": f"将正常目标 {nid} 误判为幽灵"})
            
            # 检查是否包含虚构的 ID
            for aid in agent_ghost_ids:
                if aid not in ground_truth_ghosts and aid not in ground_truth_normals:
                    score -= 5
                    details.append({"item": f"虚构检测 ID {aid}", "score": -5, "max_score": 0, "passed": False, "reason": "结果中包含数据中不存在的 ID"})

        except Exception as e:
            details.append({"item": "解析文件异常", "score": 0, "max_score": 80, "passed": False, "reason": str(e)})
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 100, "passed": False, "reason": "找不到 calibration/ghost_ids.txt"})

    # 最终分修正
    score = max(0, min(100, score))
    return score, details

if __name__ == "__main__":
    total_score, score_details = verify()
    output = {
        "total_score": total_score,
        "details": score_details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
