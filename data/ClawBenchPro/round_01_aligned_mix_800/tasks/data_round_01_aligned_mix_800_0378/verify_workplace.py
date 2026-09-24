import os
import sys
import json
import re

def verify_results(workspace):
    score = 0
    details = []
    
    target_dir = os.path.join(workspace, "secure_vault")
    target_file = os.path.join(target_dir, "compliance_audit.json")
    
    # 1. 检查目录与文件物理存在性 (10分)
    if os.path.exists(target_dir) and os.path.isdir(target_dir):
        score += 5
        details.append({"item": "检查 secure_vault 目录", "score": 5, "max_score": 5, "passed": True, "reason": "目录已创建"})
    else:
        details.append({"item": "检查 secure_vault 目录", "score": 0, "max_score": 5, "passed": False, "reason": "目录缺失"})

    if os.path.exists(target_file):
        score += 5
        details.append({"item": "检查 compliance_audit.json 文件", "score": 5, "max_score": 5, "passed": True, "reason": "文件已创建"})
    else:
        details.append({"item": "检查 compliance_audit.json 文件", "score": 0, "max_score": 5, "passed": False, "reason": "文件未生成"})
        # 如果文件不存在，后续检查无法进行，直接输出
        save_results(score, details)
        return

    # 2. 检查 JSON 格式合法性 (10分)
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score += 10
        details.append({"item": "检查 JSON 格式", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
    except Exception as e:
        details.append({"item": "检查 JSON 格式", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        save_results(score, details)
        return

    # 3. 核心业务逻辑验证：医生 ID 映射与违规计数 (70分)
    # 预期结果 (基于 env_builder.py 内容推导):
    # DOC-101 (PAGER-8832): batch_A 2个, batch_B 1个 -> 共 3 个
    # DOC-339 (PAGER-1122): batch_B 1个 -> 共 1 个
    # DOC-492 (PAGER-4455): batch_B 1个, batch_C 1个 -> 共 2 个
    # DOC-204 (PAGER-9911): 0个 (虽然有 SSN 字眼但无格式)
    # DOC-505 (PAGER-7766): 0个 (只有电话号码)
    expected_mapping = {
        "DOC-101": 3,
        "DOC-339": 1,
        "DOC-492": 2
    }
    
    # 检查是否包含所有违规医生且计数准确
    correct_doctors = 0
    total_doctors = len(expected_mapping)
    
    for doc_id, count in expected_mapping.items():
        if doc_id in data:
            if data[doc_id] == count:
                correct_doctors += 1
            else:
                details.append({"item": f"检查 {doc_id} 违规计数", "score": 0, "max_score": 0, "passed": False, "reason": f"期望 {count}, 实际 {data[doc_id]}"})
        else:
            details.append({"item": f"检查 {doc_id} 是否存在", "score": 0, "max_score": 0, "passed": False, "reason": "未找到该医生记录"})

    mapping_score = int((correct_doctors / total_doctors) * 70)
    score += mapping_score
    details.append({"item": "关键数据映射与计数准确度", "score": mapping_score, "max_score": 70, "passed": correct_doctors == total_doctors, "reason": f"正确匹配 {correct_doctors}/{total_doctors} 个医生"})

    # 4. 检查是否有幻觉数据 (10分)
    # 如果 JSON 中包含不在预期内的医生（如计入了 0 违规的医生），或格式完全错误的 Key
    illegal_keys = [k for k in data.keys() if k not in expected_mapping]
    if not illegal_keys:
        score += 10
        details.append({"item": "排除多余/错误数据", "score": 10, "max_score": 10, "passed": True, "reason": "未发现多余数据"})
    else:
        # 每多一个错误 Key 扣 5 分，扣完为止
        penalty = min(10, len(illegal_keys) * 5)
        score += (10 - penalty)
        details.append({"item": "排除多余/错误数据", "score": 10 - penalty, "max_score": 10, "passed": False, "reason": f"包含多余/错误医生 ID: {illegal_keys}"})

    save_results(score, details)

def save_results(score, details):
    output = {
        "total_score": max(0, min(100, score)),
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_results(workspace_path)
