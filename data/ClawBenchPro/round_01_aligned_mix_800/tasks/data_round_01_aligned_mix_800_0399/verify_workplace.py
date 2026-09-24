import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    target_file = os.path.join(workspace, "organized_desk", "residential_summary.json")
    
    # 1. 检查目标文件与目录是否存在 (15分)
    if os.path.exists(target_file):
        total_score += 15
        score_details.append({
            "item": "验证目标文件生成", 
            "score": 15, 
            "max_score": 15, 
            "passed": True, 
            "reason": "成功在 organized_desk 目录下生成 residential_summary.json"
        })
    else:
        score_details.append({
            "item": "验证目标文件生成", 
            "score": 0, 
            "max_score": 15, 
            "passed": False, 
            "reason": "未找到 organized_desk/residential_summary.json 文件"
        })
        dump_score(total_score, score_details)
        return
        
    # 2. 检查 JSON 结构合法性 (15分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            total_score += 15
            score_details.append({
                "item": "JSON Schema 校验", 
                "score": 15, 
                "max_score": 15, 
                "passed": True, 
                "reason": "JSON 结构正确，根节点为列表类型"
            })
        else:
            score_details.append({
                "item": "JSON Schema 校验", 
                "score": 0, 
                "max_score": 15, 
                "passed": False, 
                "reason": "JSON 格式错误：根节点必须是 List"
            })
            dump_score(total_score, score_details)
            return
    except Exception as e:
        score_details.append({
            "item": "JSON Schema 校验", 
            "score": 0, 
            "max_score": 15, 
            "passed": False, 
            "reason": f"无法读取或解析 JSON 文件: {str(e)}"
        })
        dump_score(total_score, score_details)
        return

    # 3. 校验实体过滤与核心数据完整性 (30分)
    # 应包含: Arthur (PT-8829), Martha (PT-3344), Billy (PT-5566), Chloe (PT-9900)
    # 不应包含: Sarah (PT-1122), Greg (PT-7788), Dave (PT-2211)
    names_found = [str(item.get("name", "")).lower() for item in data]
    expected_residents = ["arthur", "martha", "billy", "chloe"]
    expected_outpatients = ["sarah", "greg", "dave"]
    
    residents_matched = sum(1 for r in expected_residents if any(r in n for n in names_found))
    outpatients_included = sum(1 for o in expected_outpatients if any(o in n for n in names_found))
    
    filter_score = 0
    # 常驻病患召回率（满分15分）
    filter_score += int(15 * (residents_matched / 4))
    # 门诊病患剔除率（满分15分，错误包含则扣分）
    filter_score += max(0, 15 - (5 * outpatients_included))
    
    total_score += filter_score
    score_details.append({
        "item": "患者状态精准过滤 (Resident only)", 
        "score": filter_score, 
        "max_score": 30, 
        "passed": filter_score == 30, 
        "reason": f"正确召回 {residents_matched}/4 个常驻病患，错误包含了 {outpatients_included} 个门诊病患。"
    })

    # 4. 校验疼痛指数的深度清理 (20分)
    # 要求：纯数字，不能带有 /10
    pain_correct = 0
    for item in data:
        pain = str(item.get("pain_level", "")).strip()
        if pain and "/" not in pain and pain.isdigit():
            pain_correct += 1
            
    pain_score = 0
    if len(data) > 0:
        pain_score = int(20 * (pain_correct / len(data)))
    
    total_score += pain_score
    score_details.append({
        "item": "数据清洗: 提取纯数字疼痛指数", 
        "score": pain_score, 
        "max_score": 20, 
        "passed": pain_score == 20, 
        "reason": f"{pain_correct}/{len(data)} 个记录的 pain_level 成功剔除了冗余字符格式。"
    })

    # 5. 正念冥想干预标记的逻辑校验 (20分)
    # Arthur (stressed)->True, Martha (no keyword)->False, Billy (tense)->True, Chloe (yoga)->True
    expected_candidates = {"arthur": True, "martha": False, "billy": True, "chloe": True}
    candidate_matches = 0
    
    for item in data:
        name = str(item.get("name", "")).lower()
        candidate = item.get("mindfulness_candidate")
        for k, v_expected in expected_candidates.items():
            if k in name and candidate == v_expected:
                candidate_matches += 1
                break
                
    candidate_score = 0
    if residents_matched > 0:
        candidate_score = int(20 * (candidate_matches / max(residents_matched, 1)))
        
    total_score += candidate_score
    score_details.append({
        "item": "业务逻辑推导: Mindfulness Candidate 标记", 
        "score": candidate_score, 
        "max_score": 20, 
        "passed": candidate_score == 20, 
        "reason": f"{candidate_matches} 个候选人状态标记正确（基于详细笔记内容的关键字精确匹配）。"
    })

    dump_score(total_score, score_details)

def dump_score(total, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total, "details": details}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
