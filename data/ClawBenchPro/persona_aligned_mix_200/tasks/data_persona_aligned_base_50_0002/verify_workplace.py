import os
import sys
import json

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "ci_patch/conflict_report.json")
    
    score = 0
    details = []

    # 1. Check if the directory and file exist (10 points)
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 ci_patch/conflict_report.json 存在"})
        
        # 2. Check if the file is valid JSON (10 points)
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            score += 10
            details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
            
            # 3. Check for required fields (10 points)
            required_fields = ["package", "version_a", "version_b"]
            missing_fields = [f for f in required_fields if f not in data]
            if not missing_fields:
                score += 10
                details.append({"item": "检查必填字段", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有必需字段"})
                
                # 4. Check package name (30 points)
                # Allow case-insensitive check and trim
                actual_package = str(data.get("package", "")).strip().lower()
                expected_package = "eigen_matrix"
                if actual_package == expected_package:
                    score += 30
                    details.append({"item": "验证冲突包名", "score": 30, "max_score": 30, "passed": True, "reason": f"匹配正确: {expected_package}"})
                else:
                    details.append({"item": "验证冲突包名", "score": 0, "max_score": 30, "passed": False, "reason": f"期望 {expected_package}, 实际为 {actual_package}"})

                # 5. Check versions (20 + 20 points)
                # Versions might be swapped, we accept both orders
                actual_versions = sorted([str(data.get("version_a", "")), str(data.get("version_b", ""))])
                expected_versions = sorted(["3.3.9", "3.4.2"])
                
                if actual_versions[0] == expected_versions[0]:
                    score += 20
                    details.append({"item": "验证版本号 A", "score": 20, "max_score": 20, "passed": True, "reason": f"版本 {actual_versions[0]} 匹配成功"})
                else:
                    details.append({"item": "验证版本号 A", "score": 0, "max_score": 20, "passed": False, "reason": f"未找到版本 {expected_versions[0]}"})

                if actual_versions[1] == expected_versions[1]:
                    score += 20
                    details.append({"item": "验证版本号 B", "score": 20, "max_score": 20, "passed": True, "reason": f"版本 {actual_versions[1]} 匹配成功"})
                else:
                    details.append({"item": "验证版本号 B", "score": 0, "max_score": 20, "passed": False, "reason": f"未找到版本 {expected_versions[1]}"})

            else:
                details.append({"item": "检查必填字段", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失字段: {missing_fields}"})
                details.append({"item": "验证详细内容", "score": 0, "max_score": 70, "passed": False, "reason": "由于 JSON 字段不全，无法进行内容比对"})

        except json.JSONDecodeError:
            details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 格式错误，无法解析"})
            details.append({"item": "验证后续内容", "score": 0, "max_score": 80, "passed": False, "reason": "由于 JSON 解析失败，跳过内容验证"})
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 ci_patch/conflict_report.json 未找到"})
        details.append({"item": "验证后续所有项", "score": 0, "max_score": 90, "passed": False, "reason": "找不到目标文件"})

    # Output results
    output_data = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify_workplace()
