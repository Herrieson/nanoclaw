import os
import sys
import json
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []
    
    ioc_file_path = os.path.join(workspace, "report/ioc.json")
    
    # 1. 检查文件是否存在 (10分)
    if os.path.exists(ioc_file_path):
        score += 10
        details.append({"item": "检查 report/ioc.json 物理文件", "score": 10, "max_score": 10, "passed": True, "reason": "文件已生成"})
        
        # 2. 检查 JSON 格式合法性 (10分)
        try:
            with open(ioc_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            score += 10
            details.append({"item": "检查 JSON 语法合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
            
            # 3. 检查持久化恶意路径 (40分)
            # 期待路径: C:\ProgramData\Intel\telemetry_srv.exe
            expected_path = r"C:\ProgramData\Intel\telemetry_srv.exe".lower()
            
            found_path = False
            actual_path_val = ""
            # 遍历 JSON 寻找类似路径的字符串
            def find_path_recursive(obj):
                nonlocal found_path, actual_path_val
                if isinstance(obj, str):
                    if "telemetry_srv.exe" in obj.lower():
                        actual_path_val = obj
                        if obj.lower().replace("/", "\\") == expected_path:
                            found_path = True
                elif isinstance(obj, dict):
                    for v in obj.values(): find_path_recursive(v)
                elif isinstance(obj, list):
                    for i in obj: find_path_recursive(i)

            find_path_recursive(data)
            
            if found_path:
                score += 40
                details.append({"item": "恶意程序持久化路径匹配", "score": 40, "max_score": 40, "passed": True, "reason": f"成功提取并匹配路径: {actual_path_val}"})
            elif "telemetry_srv.exe" in actual_path_val.lower():
                score += 20
                details.append({"item": "恶意程序持久化路径匹配", "score": 20, "max_score": 40, "passed": False, "reason": f"提取到的路径不完整或不准确: {actual_path_val}"})
            else:
                details.append({"item": "恶意程序持久化路径匹配", "score": 0, "max_score": 40, "passed": False, "reason": "未找到正确的恶意程序路径"})

            # 4. 检查脱壳特征码 (40分)
            # 期待特征码: 5C7A8E1F2B3D4C5A6B7C8D9EAFB0C1D2 (16字节)
            expected_sig = "5c7a8e1f2b3d4c5a6b7c8d9eafb0c1d2"
            
            found_sig = False
            actual_sig_val = ""
            
            def find_sig_recursive(obj):
                nonlocal found_sig, actual_sig_val
                if isinstance(obj, str):
                    # 移除空格、破折号、0x等干扰项进行匹配
                    clean_str = re.sub(r'[^a-fA-F0-9]', '', obj).lower()
                    if expected_sig in clean_str:
                        actual_sig_val = obj
                        found_sig = True
                elif isinstance(obj, dict):
                    for v in obj.values(): find_sig_recursive(v)
                elif isinstance(obj, list):
                    for i in obj: find_sig_recursive(i)
            
            find_sig_recursive(data)
            
            if found_sig:
                score += 40
                details.append({"item": "16字节脱壳特征码匹配", "score": 40, "max_score": 40, "passed": True, "reason": f"成功匹配特征码: {actual_sig_val}"})
            else:
                details.append({"item": "16字节脱壳特征码匹配", "score": 0, "max_score": 40, "passed": False, "reason": "未找到或特征码错误"})

        except json.JSONDecodeError:
            details.append({"item": "检查 JSON 语法合法性", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 格式错误，无法解析"})
            details.append({"item": "数据内容检查", "score": 0, "max_score": 80, "passed": False, "reason": "由于 JSON 无法解析，跳过内容检查"})
    else:
        details.append({"item": "检查 report/ioc.json 物理文件", "score": 0, "max_score": 10, "passed": False, "reason": "文件未生成"})
        details.append({"item": "后续所有检查", "score": 0, "max_score": 90, "passed": False, "reason": "基础文件缺失"})

    # 最终输出结果
    result = {
        "total_score": score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
