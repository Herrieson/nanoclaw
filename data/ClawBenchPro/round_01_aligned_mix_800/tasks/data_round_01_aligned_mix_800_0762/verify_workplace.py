import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "final_docs", "report.json")
    
    score = 0
    details = []

    # 1. 检查文件是否存在且为合法 JSON
    if not os.path.exists(report_path):
        details.append({"item": "report.json 存在性", "score": 0, "max_score": 20, "passed": False, "reason": "文件 final_docs/report.json 不存在"})
        return write_score(score, details)
    
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        details.append({"item": "report.json 格式合法性", "score": 20, "max_score": 20, "passed": True, "reason": "成功解析为 JSON"})
        score += 20
    except json.JSONDecodeError:
        details.append({"item": "report.json 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 格式解析失败"})
        return write_score(score, details)

    # 递归提取与结构扁平化，用于容错检测
    def traverse_grades(obj):
        found = {4: False, 5: False, 6: False}
        if isinstance(obj, dict):
            # 模式 1: 键为年级，值为时长
            for k, v in obj.items():
                k_str = str(k).lower()
                if '4' in k_str and str(v) == '9': found[4] = True
                if '5' in k_str and str(v) == '8': found[5] = True
                if '6' in k_str and str(v) == '7': found[6] = True
            
            # 模式 2: { "grade": 4, "hours": 9 } 结构
            str_vals = [str(v).lower() for v in obj.values()]
            if '9' in str_vals and any('4' in v for v in str_vals): found[4] = True
            if '8' in str_vals and any('5' in v for v in str_vals): found[5] = True
            if '7' in str_vals and any('6' in v for v in str_vals): found[6] = True
            
            for v in obj.values():
                child_found = traverse_grades(v)
                for k in found: found[k] = found[k] or child_found[k]
        elif isinstance(obj, list):
            for item in obj:
                child_found = traverse_grades(item)
                for k in found: found[k] = found[k] or child_found[k]
        return found

    grade_results = traverse_grades(data)
    
    # 2. 检查 4 年级总时长 (9 小时)
    if grade_results[4]:
        details.append({"item": "Grade 4 时长统计", "score": 15, "max_score": 15, "passed": True, "reason": "准确计算出 4 年级总时长为 9"})
        score += 15
    else:
        details.append({"item": "Grade 4 时长统计", "score": 0, "max_score": 15, "passed": False, "reason": "未能准确计算出 4 年级总时长为 9"})

    # 3. 检查 5 年级总时长 (8 小时)
    if grade_results[5]:
        details.append({"item": "Grade 5 时长统计", "score": 15, "max_score": 15, "passed": True, "reason": "准确计算出 5 年级总时长为 8"})
        score += 15
    else:
        details.append({"item": "Grade 5 时长统计", "score": 0, "max_score": 15, "passed": False, "reason": "未能准确计算出 5 年级总时长为 8"})

    # 4. 检查 6 年级总时长 (7 小时)
    if grade_results[6]:
        details.append({"item": "Grade 6 时长统计", "score": 15, "max_score": 15, "passed": True, "reason": "准确计算出 6 年级总时长为 7"})
        score += 15
    else:
        details.append({"item": "Grade 6 时长统计", "score": 0, "max_score": 15, "passed": False, "reason": "未能准确计算出 6 年级总时长为 7"})

    # 获取所有文本，用于提取名字
    def get_all_strings(obj):
        strings = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                strings.append(str(k).lower())
                strings.extend(get_all_strings(v))
        elif isinstance(obj, list):
            for item in obj:
                strings.extend(get_all_strings(item))
        else:
            strings.append(str(obj).lower())
        return strings

    all_strs = get_all_strings(data)
    
    expected_missing = ['leo', 'sam', 'alex']
    not_expected = ['mia', 'zoe', 'carlos', 'chloe', 'emma', 'oliver']
    
    found_missing = [name for name in expected_missing if any(name in s for s in all_strs)]
    found_unwanted = [name for name in not_expected if any(name in s for s in all_strs)]

    # 5. 检查缺失签名的学生名单
    if len(found_missing) == 3:
        details.append({"item": "未签名学生名单", "score": 20, "max_score": 20, "passed": True, "reason": f"成功找出所有目标学生: {found_missing}"})
        score += 20
    else:
        pts = len(found_missing) * 6
        details.append({"item": "未签名学生名单", "score": pts, "max_score": 20, "passed": False, "reason": f"仅找出部分/未找出目标学生: {found_missing}"})
        score += pts

    # 6. 幻觉与冗余数据严查
    if len(found_unwanted) == 0:
        details.append({"item": "过滤冗余数据", "score": 15, "max_score": 15, "passed": True, "reason": "未将已签名或缺勤的学生混入报告"})
        score += 15
    else:
        details.append({"item": "过滤冗余数据", "score": 0, "max_score": 15, "passed": False, "reason": f"包含不应该出现的学生名字 (假阳性): {found_unwanted}"})

    write_score(score, details)

def write_score(score, details):
    output = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    verify()
