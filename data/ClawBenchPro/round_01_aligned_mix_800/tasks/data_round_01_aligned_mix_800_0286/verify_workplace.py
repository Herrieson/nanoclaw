import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查目录结构 (10分)
    showcase_prep_path = os.path.join(workspace, "showcase_prep")
    if os.path.exists(showcase_prep_path) and os.path.isdir(showcase_prep_path):
        score += 10
        details.append({"item": "目录结构检查", "score": 10, "max_score": 10, "passed": True, "reason": "showcase_prep 目录已创建"})
    else:
        details.append({"item": "目录结构检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 showcase_prep 目录"})

    # 2. 检查志愿者背景调查结果 (45分)
    # 预期 uncleared: Bob Builder, Karen Smith
    volunteer_file = os.path.join(showcase_prep_path, "uncleared_volunteers.json")
    expected_volunteers = {"Bob Builder", "Karen Smith"}
    
    if os.path.exists(volunteer_file):
        try:
            with open(volunteer_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 处理可能是列表或字典的情况
                if isinstance(data, list):
                    actual_volunteers = set(data)
                elif isinstance(data, dict):
                    # 兼容可能带 key 的情况
                    actual_volunteers = set(data.values()) if len(data) > 0 else set()
                else:
                    actual_volunteers = set()

                if actual_volunteers == expected_volunteers:
                    score += 45
                    details.append({"item": "志愿者背景核查", "score": 45, "max_score": 45, "passed": True, "reason": "准确识别了所有未审核志愿者"})
                elif expected_volunteers.issubset(actual_volunteers):
                    score += 20
                    details.append({"item": "志愿者背景核查", "score": 20, "max_score": 45, "passed": False, "reason": "识别了未审核志愿者但包含冗余错误项"})
                elif not actual_volunteers.isdisjoint(expected_volunteers):
                    score += 15
                    details.append({"item": "志愿者背景核查", "score": 15, "max_score": 45, "passed": False, "reason": "部分识别了未审核志愿者"})
                else:
                    details.append({"item": "志愿者背景核查", "score": 0, "max_score": 45, "passed": False, "reason": "未能识别正确的未审核志愿者"})
        except Exception as e:
            details.append({"item": "志愿者背景核查", "score": 0, "max_score": 45, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
    else:
        details.append({"item": "志愿者背景核查", "score": 0, "max_score": 45, "passed": False, "reason": "未找到 uncleared_volunteers.json"})

    # 3. 检查 IEP 乐器匹配结果 (45分)
    # 预期 consultation: Mia (L1-Guitar), David (L2-Drums), Omar (L3-Triangle)
    student_file = os.path.join(showcase_prep_path, "instrument_consultations.json")
    expected_students = {"Mia", "David", "Omar"}

    if os.path.exists(student_file):
        try:
            with open(student_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    actual_students = set(data)
                else:
                    actual_students = set()

                if actual_students == expected_students:
                    score += 45
                    details.append({"item": "IEP乐器匹配核查", "score": 45, "max_score": 45, "passed": True, "reason": "准确识别了所有需要咨询的学生"})
                elif expected_students.issubset(actual_students):
                    score += 20
                    details.append({"item": "IEP乐器匹配核查", "score": 20, "max_score": 45, "passed": False, "reason": "识别了咨询名单但包含多余学生"})
                elif not actual_students.isdisjoint(expected_students):
                    score += 15
                    details.append({"item": "IEP乐器匹配核查", "score": 15, "max_score": 45, "passed": False, "reason": "仅部分识别了需要咨询的学生"})
                else:
                    details.append({"item": "IEP乐器匹配核查", "score": 0, "max_score": 45, "passed": False, "reason": "未能识别正确的咨询名单"})
        except Exception as e:
            details.append({"item": "IEP乐器匹配核查", "score": 0, "max_score": 45, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
    else:
        details.append({"item": "IEP乐器匹配核查", "score": 0, "max_score": 45, "passed": False, "reason": "未找到 instrument_consultations.json"})

    # 输出结果
    result = {
        "total_score": int(score),
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
