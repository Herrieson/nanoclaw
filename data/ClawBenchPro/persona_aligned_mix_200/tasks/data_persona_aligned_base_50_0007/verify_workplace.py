import os
import sys
import json
import math

def calculate_expected_norm(fx, fy, fz):
    return math.sqrt(fx**2 + fy**2 + fz**2)

def verify():
    # 默认工作区路径获取
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "report/culprit.json")
    score_file = "workplace_score.json"
    
    total_score = 0
    details = []

    # 预设的正确答案（基于 env_builder.py）
    EXPECTED_STEP = 14
    EXPECTED_ATOM_IDX = 42
    # fx, fy, fz = 845.210, -991.330, 1502.440
    EXPECTED_FORCE_NORM = calculate_expected_norm(845.210, -991.330, 1502.440) # 约 1988.577...

    # 1. 检查目录和文件是否存在 (10分)
    if os.path.exists(report_path):
        score_1 = 10
        details.append({"item": "检查报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到 report/culprit.json"})
    else:
        score_1 = 0
        details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 report/culprit.json"})
        # 如果文件不存在，后续检查无法进行，直接写入结果
        with open(score_file, "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2)
        return

    # 2. 检查 JSON 格式合法性 (10分)
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score_2 = 10
        details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
    except Exception as e:
        score_2 = 0
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        with open(score_file, "w") as f:
            json.dump({"total_score": score_1, "details": details}, f, indent=2)
        return

    # 3. 验证离子步序号 (20分)
    # 字段名可能不唯一，允许 agent 使用常用字段名，但优先匹配题目要求的逻辑
    step_keys = ["ionic_step", "step", "step_number", "fatal_step"]
    found_step = None
    for k in step_keys:
        if k in data:
            found_step = data[k]
            break
    
    if found_step == EXPECTED_STEP:
        score_3 = 20
        details.append({"item": "验证致命离子步序号", "score": 20, "max_score": 20, "passed": True, "reason": f"离子步序号正确: {found_step}"})
    else:
        score_3 = 0
        details.append({"item": "验证致命离子步序号", "score": 0, "max_score": 20, "passed": False, "reason": f"序号错误或缺失，期望 {EXPECTED_STEP}，实际拿到 {found_step}"})

    # 4. 验证原子索引 (30分)
    atom_keys = ["atom_index", "culprit_atom", "atom_id", "atom_idx"]
    found_atom = None
    for k in atom_keys:
        if k in data:
            found_atom = data[k]
            break
    
    if found_atom == EXPECTED_ATOM_IDX:
        score_4 = 30
        details.append({"item": "验证异常原子索引", "score": 30, "max_score": 30, "passed": True, "reason": f"原子索引正确: {found_atom}"})
    else:
        score_4 = 0
        details.append({"item": "验证异常原子索引", "score": 0, "max_score": 30, "passed": False, "reason": f"索引错误或缺失，期望 {EXPECTED_ATOM_IDX}，实际拿到 {found_atom}"})

    # 5. 验证受力大小 (30分)
    force_keys = ["force_magnitude", "force_norm", "max_force", "force"]
    found_force = None
    for k in force_keys:
        if k in data:
            found_force = data[k]
            break
    
    if found_force is not None:
        try:
            val = float(found_force)
            if math.isclose(val, EXPECTED_FORCE_NORM, rel_tol=1e-3):
                score_5 = 30
                details.append({"item": "验证受力绝对值计算", "score": 30, "max_score": 30, "passed": True, "reason": f"受力大小符合预期: {val}"})
            else:
                score_5 = 0
                details.append({"item": "验证受力绝对值计算", "score": 0, "max_score": 30, "passed": False, "reason": f"数值偏差过大，期望约 {EXPECTED_FORCE_NORM:.4f}, 实际为 {val}"})
        except:
            score_5 = 0
            details.append({"item": "验证受力绝对值计算", "score": 0, "max_score": 30, "passed": False, "reason": "受力字段无法转换为浮点数"})
    else:
        score_5 = 0
        details.append({"item": "验证受力绝对值计算", "score": 0, "max_score": 30, "passed": False, "reason": "未找到受力大小字段"})

    # 汇总
    total_score = score_1 + score_2 + score_3 + score_4 + score_5
    
    # 额外检查：如果 Agent 提供了多余的虚假字段（如猜测的化学元素等题目没给的信息），酌情扣分 (可选防御性逻辑)
    if len(data) > 6:
         total_score = max(0, total_score - 5)
         details.append({"item": "冗余信息惩罚", "score": -5, "max_score": 0, "passed": False, "reason": "JSON中包含过量未要求的字段，可能存在幻觉"})

    with open(score_file, "w") as f:
        json.dump({"total_score": int(total_score), "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
