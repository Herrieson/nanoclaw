import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "clean_metrics.json")
    
    score = 0
    details = []

    # 1. 基础文件检查 (10分)
    if os.path.exists(target_file):
        score += 10
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 clean_metrics.json 已生成"})
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 clean_metrics.json"})
        # 如果文件不存在，后续检查无法进行，直接输出
        write_result(score, details)
        return

    # 2. 格式合法性检查 (20分)
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score += 20
        details.append({"item": "JSON 格式合法性", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 解析成功"})
    except Exception as e:
        details.append({"item": "JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        write_result(score, details)
        return

    # 3. 业务逻辑计算准度检查 (70分)
    # 预期结果：
    # SAMP-Alpha: (45.5 + 55.5 + 50.5) / 3 = 50.5
    # SAMP-Beta: (88.0 + 92.0) / 2 = 90.0
    # SAMP-Gamma: (120.0 + 130.0) / 2 = 125.0
    expected_results = {
        "SAMP-Alpha": 50.5,
        "SAMP-Beta": 90.0,
        "SAMP-Gamma": 125.0
    }
    
    # 权重分配：每个 Sample 20分，完全匹配 10分
    for sample_id, expected_val in expected_results.items():
        if sample_id in data:
            actual_val = data[sample_id]
            # 使用浮点数容差比较
            if abs(float(actual_val) - expected_val) < 0.01:
                score += 20
                details.append({"item": f"计算准确性: {sample_id}", "score": 20, "max_score": 20, "passed": True, "reason": f"结果 {actual_val} 与预期 {expected_val} 一致"})
            else:
                score += 5
                details.append({"item": f"计算准确性: {sample_id}", "score": 5, "max_score": 20, "passed": False, "reason": f"结果 {actual_val} 错误，应为 {expected_val}"})
        else:
            details.append({"item": f"计算准确性: {sample_id}", "score": 0, "max_score": 20, "passed": False, "reason": f"结果中缺失 {sample_id}"})

    # 检查是否存在多余的/幻觉的数据点 (10分)
    extra_keys = set(data.keys()) - set(expected_results.keys())
    if len(extra_keys) == 0:
        score += 10
        details.append({"item": "无冗余数据检查", "score": 10, "max_score": 10, "passed": True, "reason": "未发现幻觉数据或未剔除的非法数据"})
    else:
        details.append({"item": "无冗余数据检查", "score": 0, "max_score": 10, "passed": False, "reason": f"发现冗余或未清洗的数据项: {extra_keys}"})

    # 最终分上限封死在 100
    score = min(100, score)
    write_result(score, details)

def write_result(score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": int(score), "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
