import os
import sys
import json

def verify_workplace(workspace):
    score = 0
    details = []

    target_dir = os.path.join(workspace, "bug_report")
    target_file = os.path.join(target_dir, "culprit_symbol.txt")
    
    # 1. 检查目录和文件是否存在 (10分)
    if os.path.exists(target_dir) and os.path.exists(target_file):
        score += 10
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 bug_report/culprit_symbol.txt 已生成"})
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 bug_report/culprit_symbol.txt"})
        # 如果文件不存在，后续检查无法进行
        save_score(score, details)
        return

    # 2. 检查文件内容是否正确 (80分)
    # 目标符号是 update_hardware_watchdog
    correct_symbol = "update_hardware_watchdog"
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if content == correct_symbol:
            score += 80
            details.append({"item": "检查符号名称是否匹配", "score": 80, "max_score": 80, "passed": True, "reason": f"成功定位到错误符号：{correct_symbol}"})
        elif correct_symbol in content and len(content) < 50:
            # 允许一些轻微的格式偏差，但扣分
            score += 40
            details.append({"item": "检查符号名称是否匹配", "score": 40, "max_score": 80, "passed": True, "reason": f"找到了正确符号但文件格式不符合‘纯文本’要求：{content}"})
        else:
            details.append({"item": "检查符号名称是否匹配", "score": 0, "max_score": 80, "passed": False, "reason": f"符号不匹配。预期：{correct_symbol}，实际：{content}"})
    except Exception as e:
        details.append({"item": "读取文件内容", "score": 0, "max_score": 80, "passed": False, "reason": f"读取失败: {str(e)}"})

    # 3. 检查文件整洁度 (10分)
    # 提示词要求“纯文本形式”，不应包含括号、参数或长篇大论
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        if "(" in raw_content or ")" in raw_content or "\n" in raw_content.strip():
            details.append({"item": "检查输出格式整洁度", "score": 0, "max_score": 10, "passed": False, "reason": "文件中包含了多余的括号、换行或参数信息"})
        else:
            score += 10
            details.append({"item": "检查输出格式整洁度", "score": 10, "max_score": 10, "passed": True, "reason": "文件内容简洁，仅包含符号名"})
    except:
        pass

    save_score(score, details)

def save_score(score, details):
    output = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
