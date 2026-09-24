import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    file_path = os.path.join(workspace, "deliverables", "final_roster.json")
    
    # 1. Check directory and file existence (10 points)
    if os.path.exists(file_path):
        score_details.append({"item": "检查 final_roster.json 是否存在于 deliverables 目录", "score": 10, "max_score": 10, "passed": True, "reason": "文件和目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 final_roster.json 是否存在于 deliverables 目录", "score": 0, "max_score": 10, "passed": False, "reason": "文件或目录缺失"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=4)
        return
        
    # 2. Check JSON validity and schema (10 points)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        has_matched = "matched" in data and isinstance(data["matched"], (list, dict))
        has_unmatched = "unmatched" in data and isinstance(data["unmatched"], list)
        
        if has_matched and has_unmatched:
            score_details.append({"item": "检查 JSON 格式合法性及包含核心字段", "score": 10, "max_score": 10, "passed": True, "reason": "格式正确，包含 matched 和 unmatched"})
            total_score += 10
        else:
            score_details.append({"item": "检查 JSON 格式合法性及包含核心字段", "score": 0, "max_score": 10, "passed": False, "reason": "缺失 matched 或 unmatched 字段或类型不符"})
            with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
                json.dump({"total_score": total_score, "details": score_details}, f, indent=4)
            return
    except Exception as e:
        score_details.append({"item": "检查 JSON 格式合法性及包含核心字段", "score": 0, "max_score": 10, "passed": False, "reason": f"无法解析 JSON: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=4)
        return

    # Normalize matched data into a dictionary of {student: teacher}
    matched_dict = {}
    if isinstance(data["matched"], dict):
        matched_dict = data["matched"]
    else:
        for item in data["matched"]:
            if isinstance(item, dict) and "student_name" in item and "instructor_name" in item:
                matched_dict[item["student_name"]] = item["instructor_name"]
            elif isinstance(item, dict) and len(item) == 1:
                student = list(item.keys())[0]
                matched_dict[student] = item[student]

    unmatched_list = data["unmatched"]

    # Defined ground truths
    sped_students = {
        "Leo": ["Sarah"],         # Guitar + SPED
        "Mia": ["Elena"],         # Piano + SPED
        "Sam": ["Joao"],          # Drums + SPED
        "Noah": ["Elena"],        # Piano + SPED
        "Mateo": ["Sarah"]        # Bass + SPED
    }
    
    general_students = {
        "Emma": ["Sarah", "David"],  # Guitar
        "Chloe": ["Elena", "David"], # Vocals
        "Zoe": ["Miguel", "Joao"]    # Drums
    }
    
    all_known_students = set(sped_students.keys()) | set(general_students.keys()) | {"Lucas"}

    # 3. Check unmatched assignment (20 points)
    # Lucas needs Violin, but no teacher teaches Violin. Should be unmatched.
    if "Lucas" in unmatched_list and len(unmatched_list) == 1:
        score_details.append({"item": "精准验证 unmatched 列表 (仅包含 Lucas)", "score": 20, "max_score": 20, "passed": True, "reason": "Lucas 正确归为 unmatched 且无多余捏造"})
        total_score += 20
    elif "Lucas" in unmatched_list:
        score_details.append({"item": "精准验证 unmatched 列表 (仅包含 Lucas)", "score": 10, "max_score": 20, "passed": False, "reason": "Lucas 在 unmatched 中，但列表中有其他错误归类的学生"})
        total_score += 10
    else:
        score_details.append({"item": "精准验证 unmatched 列表 (仅包含 Lucas)", "score": 0, "max_score": 20, "passed": False, "reason": "Lucas 没有被正确放入 unmatched 列表"})

    # 4. Check SPED student matching (40 points)
    sped_correct = 0
    sped_errors = []
    for student, valid_teachers in sped_students.items():
        if student in matched_dict and matched_dict[student] in valid_teachers:
            sped_correct += 1
        else:
            sped_errors.append(f"{student} 错配给 {matched_dict.get(student, '未分配')}")
            
    sped_score = int(40 * (sped_correct / len(sped_students)))
    score_details.append({
        "item": "验证特需儿童被精准分配给持有 SPED 证书及对应乐器的教师", 
        "score": sped_score, 
        "max_score": 40, 
        "passed": sped_score == 40, 
        "reason": f"答对 {sped_correct}/{len(sped_students)} 个特需儿童分配。错误细节: {', '.join(sped_errors) if sped_errors else '无'}"
    })
    total_score += sped_score

    # 5. Check general student matching (20 points)
    gen_correct = 0
    gen_errors = []
    for student, valid_teachers in general_students.items():
        if student in matched_dict and matched_dict[student] in valid_teachers:
            gen_correct += 1
        else:
            gen_errors.append(f"{student} 错配给 {matched_dict.get(student, '未分配')}")
            
    gen_score = int(20 * (gen_correct / len(general_students)))
    score_details.append({
        "item": "验证常规需求儿童被正确分配给对应乐器的教师", 
        "score": gen_score, 
        "max_score": 20, 
        "passed": gen_score == 20, 
        "reason": f"答对 {gen_correct}/{len(general_students)} 个常规儿童分配。错误细节: {', '.join(gen_errors) if gen_errors else '无'}"
    })
    total_score += gen_score

    # Check for hallucinations
    assigned_students = set(matched_dict.keys()) | set(unmatched_list)
    hallucinated = assigned_students - all_known_students
    if hallucinated:
        deduct = min(total_score, 20)
        total_score -= deduct
        score_details.append({"item": "反作弊/幻觉检测", "score": -deduct, "max_score": 0, "passed": False, "reason": f"捏造了不存在的注册学生数据: {hallucinated}"})
    
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=4)

if __name__ == "__main__":
    verify()
