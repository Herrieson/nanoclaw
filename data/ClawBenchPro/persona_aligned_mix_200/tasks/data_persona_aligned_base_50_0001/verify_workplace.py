import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "triage", "conflict_target.json")
    
    score = 0
    details = []

    # 1. 检查文件是否存在与基础格式 (10分)
    if os.path.exists(target_file):
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            score += 10
            details.append({"item": "JSON文件存在且格式正确", "score": 10, "max_score": 10, "passed": True, "reason": "文件读取成功"})
        except Exception as e:
            details.append({"item": "JSON文件格式解析", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
            data = {}
    else:
        details.append({"item": "JSON文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 triage/conflict_target.json"})
        data = {}

    # 预定义的标准答案 (根据 env_builder.py 的逻辑)
    # 冲突发生点：node-beta 在收到 node-gamma (T5) 的心跳时，本地 index 100 的 term 是 4
    expected_node = "node-beta"
    expected_term = 4
    expected_index = 100

    # 2. 检查 node_id (30分)
    node_id = data.get("node_id")
    if node_id == expected_node:
        score += 30
        details.append({"item": "匹配冲突节点 ID", "score": 30, "max_score": 30, "passed": True, "reason": f"成功识别节点: {node_id}"})
    else:
        details.append({"item": "匹配冲突节点 ID", "score": 0, "max_score": 30, "passed": False, "reason": f"期望 {expected_node}, 实际得到 {node_id}"})

    # 3. 检查 conflict_term (30分)
    try:
        term = int(data.get("conflict_term", -1))
        if term == expected_term:
            score += 30
            details.append({"item": "匹配冲突任期号 (Term)", "score": 30, "max_score": 30, "passed": True, "reason": f"成功识别任期: {term}"})
        else:
            details.append({"item": "匹配冲突任期号 (Term)", "score": 0, "max_score": 30, "passed": False, "reason": f"期望 {expected_term}, 实际得到 {term}"})
    except (ValueError, TypeError):
        details.append({"item": "匹配冲突任期号 (Term)", "score": 0, "max_score": 30, "passed": False, "reason": "任期号缺失或非整数"})

    # 4. 检查 conflict_index (30分)
    try:
        idx = int(data.get("conflict_index", -1))
        if idx == expected_index:
            score += 30
            details.append({"item": "匹配冲突日志索引 (Log Index)", "score": 30, "max_score": 30, "passed": True, "reason": f"成功识别索引: {idx}"})
        else:
            details.append({"item": "匹配冲突日志索引 (Log Index)", "score": 0, "max_score": 30, "passed": False, "reason": f"期望 {expected_index}, 实际得到 {idx}"})
    except (ValueError, TypeError):
        details.append({"item": "匹配冲突日志索引 (Log Index)", "score": 0, "max_score": 30, "passed": False, "reason": "索引号缺失或非整数"})

    # 结果写入
    output_file = "workplace_score.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
