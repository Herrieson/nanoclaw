import os
import sys
import json

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "iocs/extracted_iocs.json")
    score_file = os.path.join(workspace, "workplace_score.json")
    
    total_score = 0
    details = []

    # 1. 检查文件是否存在与基本 JSON 格式 (10分)
    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            total_score += 10
            details.append({"item": "文件存在与JSON格式", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析 JSON 文件"})
        except Exception as e:
            details.append({"item": "文件存在与JSON格式", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
            data = {}
    else:
        details.append({"item": "文件存在与JSON格式", "score": 0, "max_score": 10, "passed": False, "reason": "iocs/extracted_iocs.json 不存在"})
        data = {}

    # 2. 检查 registry_value (30分)
    expected_reg = "WinUpdateSvc"
    actual_reg = data.get("registry_value")
    if actual_reg == expected_reg:
        total_score += 30
        details.append({"item": "注册表键名提取", "score": 30, "max_score": 30, "passed": True, "reason": "registry_value 正确"})
    else:
        details.append({"item": "注册表键名提取", "score": 0, "max_score": 30, "passed": False, "reason": f"预期 '{expected_reg}', 实际得到 '{actual_reg}'"})

    # 3. 检查 malicious_path (30分)
    expected_path = "C:\\Users\\Public\\winlogon.exe"
    actual_path = data.get("malicious_path")
    if actual_path == expected_path:
        total_score += 30
        details.append({"item": "恶意载荷路径提取", "score": 30, "max_score": 30, "passed": True, "reason": "malicious_path 正确"})
    else:
        details.append({"item": "恶意载荷路径提取", "score": 0, "max_score": 30, "passed": False, "reason": f"预期 '{expected_path}', 实际得到 '{actual_path}'"})

    # 4. 检查 unpack_signature (30分)
    # 原始字节: [0xE8, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
    expected_sig = "E8112233445566778899AABBCCDDEEFF"
    actual_sig = data.get("unpack_signature")
    
    if actual_sig == expected_sig:
        total_score += 30
        details.append({"item": "脱壳特征码提取", "score": 30, "max_score": 30, "passed": True, "reason": "unpack_signature 匹配成功 (包含跨行处理验证)"})
    elif actual_sig and actual_sig.upper() == expected_sig:
        total_score += 25
        details.append({"item": "脱壳特征码提取", "score": 25, "max_score": 30, "passed": True, "reason": "特征码内容正确但未按要求强制大写"})
    else:
        details.append({"item": "脱壳特征码提取", "score": 0, "max_score": 30, "passed": False, "reason": f"预期 '{expected_sig}', 实际得到 '{actual_sig}'"})

    # 结果写入
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify_workplace()
