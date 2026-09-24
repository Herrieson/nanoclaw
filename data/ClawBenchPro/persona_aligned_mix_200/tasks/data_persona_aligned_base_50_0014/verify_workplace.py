import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "report/root_cause.json")
    score = 0
    details = []

    # 1. Check Directory and File Existence (10 points)
    if os.path.exists(os.path.join(workspace, "report")):
        score += 5
        details.append({"item": "检查报告目录", "score": 5, "max_score": 5, "passed": True, "reason": "目录 report 存在"})
    else:
        details.append({"item": "检查报告目录", "score": 0, "max_score": 5, "passed": False, "reason": "目录 report 不存在"})

    if os.path.exists(report_path):
        score += 5
        details.append({"item": "检查报告文件是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件 root_cause.json 存在"})
    else:
        details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件 root_cause.json 不存在"})
        # If the file doesn't exist, we can't perform further checks
        save_results(score, details)
        return

    # 2. JSON Validity and Structure (20 points)
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score += 10
        details.append({"item": "检查JSON格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
        
        required_keys = ["device_address", "register_address", "illegal_value"]
        missing_keys = [k for k in required_keys if k not in data]
        if not missing_keys:
            score += 10
            details.append({"item": "检查JSON关键字段", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有必需字段"})
        else:
            details.append({"item": "检查JSON关键字段", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失字段: {missing_keys}"})
    except Exception as e:
        details.append({"item": "检查JSON格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
        save_results(score, details)
        return

    # 3. Content Accuracy (70 points)
    # Target Values based on env_builder.py: 
    # device_address: 0x5C, register_address: 0x10, illegal_value: 0x4B
    
    def normalize_hex(val):
        if not isinstance(val, str): return None
        try:
            return hex(int(val, 16)).lower()
        except:
            return None

    dev_addr = normalize_hex(data.get("device_address"))
    reg_addr = normalize_hex(data.get("register_address"))
    ill_val = normalize_hex(data.get("illegal_value"))

    # Device Address (20 points)
    if dev_addr == "0x5c":
        score += 20
        details.append({"item": "验证设备地址 (device_address)", "score": 20, "max_score": 20, "passed": True, "reason": "正确识别 PMIC 地址 0x5C"})
    else:
        details.append({"item": "验证设备地址 (device_address)", "score": 0, "max_score": 20, "passed": False, "reason": f"预期 0x5C, 实际得到 {data.get('device_address')}"})

    # Register Address (20 points)
    if reg_addr == "0x10":
        score += 20
        details.append({"item": "验证寄存器地址 (register_address)", "score": 20, "max_score": 20, "passed": True, "reason": "正确识别核心电压寄存器 0x10"})
    else:
        details.append({"item": "验证寄存器地址 (register_address)", "score": 0, "max_score": 20, "passed": False, "reason": f"预期 0x10, 实际得到 {data.get('register_address')}"})

    # Illegal Value (30 points)
    if ill_val == "0x4b":
        score += 30
        details.append({"item": "验证非法写入值 (illegal_value)", "score": 30, "max_score": 30, "passed": True, "reason": "正确锁定导致崩溃的非法值 0x4B (超过 0x3F)"})
    else:
        details.append({"item": "验证非法写入值 (illegal_value)", "score": 0, "max_score": 30, "passed": False, "reason": f"预期 0x4B, 实际得到 {data.get('illegal_value')}"})

    save_results(score, details)

def save_results(score, details):
    output = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
