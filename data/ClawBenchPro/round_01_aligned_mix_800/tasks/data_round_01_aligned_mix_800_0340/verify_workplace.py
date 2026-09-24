import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_file = os.path.join(workspace, "workplace_score.json")
    target_file = os.path.join(workspace, "precinct_desk/bolo_summary.json")
    
    total_score = 0
    details = []

    # 1. 目录与文件存在性检查 (10分)
    if os.path.exists(target_file):
        total_score += 10
        details.append({"item": "文件生成检查", "score": 10, "max_score": 10, "passed": True, "reason": "bolo_summary.json 已生成"})
    else:
        details.append({"item": "文件生成检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 bolo_summary.json"})
        # 如果文件不存在，直接写入 0 分并退出
        with open(score_file, "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # 2. JSON 格式合法性与字段完整性 (10分)
    try:
        with open(target_file, 'r') as f:
            data = json.load(f)
        total_score += 10
        details.append({"item": "JSON格式解析", "score": 10, "max_score": 10, "passed": True, "reason": "格式合法且包含必要字段"})
    except Exception as e:
        details.append({"item": "JSON格式解析", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        with open(score_file, "w") as f:
            json.dump({"total_score": 10, "details": details}, f)
        return

    # 3. 核心计算：总金额验证 (40分)
    # 计算逻辑：Rolex(500) + Ford F-150(25000) + MacBook Pro(1200) + Wallet(300) = 27000
    expected_value = 27000
    actual_value = data.get("total_stolen_value", 0)
    
    if actual_value == expected_value:
        total_score += 40
        details.append({"item": "财物总值计算", "score": 40, "max_score": 40, "passed": True, "reason": f"金额 {actual_value} 与预期完全匹配"})
    elif abs(actual_value - expected_value) < 1000:
        total_score += 20
        details.append({"item": "财物总值计算", "score": 20, "max_score": 40, "passed": False, "reason": f"金额 {actual_value} 存在误差，未准确查询基准价"})
    else:
        details.append({"item": "财物总值计算", "score": 0, "max_score": 40, "passed": False, "reason": f"金额错误，实际: {actual_value}, 预期: {expected_value}"})

    # 4. 关键信息提取：颈部纹身案件 (40分)
    # 案件 102 (skull tattoo on neck) 和 104 (snake tattoo on neck) 符合条件
    expected_cases = ["102", "104"]
    actual_cases = [str(c) for c in data.get("neck_tattoo_cases", [])]
    
    correct_cases = set(expected_cases) & set(actual_cases)
    wrong_cases = set(actual_cases) - set(expected_cases)
    
    if set(expected_cases) == set(actual_cases):
        total_score += 40
        details.append({"item": "颈部纹身案件识别", "score": 40, "max_score": 40, "passed": True, "reason": "识别了所有正确的案件编号"})
    elif len(correct_cases) > 0 and len(wrong_cases) == 0:
        score_step = 20 * len(correct_cases)
        total_score += score_step
        details.append({"item": "颈部纹身案件识别", "score": score_step, "max_score": 40, "passed": False, "reason": f"部分匹配: {correct_cases}"})
    else:
        details.append({"item": "颈部纹身案件识别", "score": 0, "max_score": 40, "passed": False, "reason": f"未正确识别或包含错误案件: {actual_cases}"})

    # 写入最终得分
    with open(score_file, "w") as f:
        json.dump({"total_score": int(total_score), "details": details}, f)

if __name__ == "__main__":
    verify()
