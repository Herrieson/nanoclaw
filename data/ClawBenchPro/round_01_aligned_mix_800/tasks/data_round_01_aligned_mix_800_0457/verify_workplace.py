import os
import sys
import json
import yaml
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 预期结果数据 (基于 env_builder.py)
    # 1. Little Bear (6): Potawatomi_Crafts, None -> Standard MRE
    # 2. Alice Morningstar (12): Navajo_Code_Talkers, None -> Standard MRE
    # 3. Cree Summer (17): Navajo_Code_Talkers, Peanuts -> Special Chow
    # 4. Billy Two-Hats (5): Potawatomi_Crafts, none -> Standard MRE
    # 5. Sky Walker (10): Potawatomi_Crafts, Shellfish -> Special Chow
    # 排除项：Sgt. Miller (Active Duty), Old Man Logan (Active Duty), Baby Yoda (3), T-1000 (19), Ghost User (STALE)

    expected_names = {"Little Bear", "Alice Morningstar", "Cree Summer", "Billy Two-Hats", "Sky Walker"}
    
    sitrep_path = os.path.join(workspace, "deliverables/sitrep.json")

    # 1. 目录与文件结构检查 (10分)
    if os.path.exists(sitrep_path):
        score += 10
        details.append({"item": "检查交付文件路径", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables/sitrep.json 存在"})
    else:
        details.append({"item": "检查交付文件路径", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables/sitrep.json"})
        # 如果文件不存在，后续检查无法进行，直接写入结果
        write_score(score, details)
        return

    # 2. JSON 格式合法性 (10分)
    try:
        with open(sitrep_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score += 10
        details.append({"item": "JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
    except Exception as e:
        details.append({"item": "JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        write_score(score, details)
        return

    # 3. 数据完整性与准确性 (50分)
    if not isinstance(data, list):
        details.append({"item": "数据结构校验", "score": 0, "max_score": 50, "passed": False, "reason": "sitrep.json 根节点应为列表"})
    else:
        found_names = {item.get("Name") for item in data if "Name" in item}
        
        # 检查是否包含多余数据 (Stale 或 Active Duty)
        extra_names = found_names - expected_names
        missing_names = expected_names - found_names
        
        accuracy_score = 0
        if not extra_names and not missing_names:
            accuracy_score = 50
            reason = "名单完全正确，无遗漏或多余项"
        elif len(extra_names) > 0:
            accuracy_score = max(0, 50 - len(extra_names) * 10)
            reason = f"包含了多余的数据（如 STALE 或 Active Duty）: {extra_names}"
        else:
            accuracy_score = max(0, 50 - len(missing_names) * 10)
            reason = f"缺失部分关键人员: {missing_names}"
        
        score += accuracy_score
        details.append({"item": "名单提取准确度", "score": int(accuracy_score), "max_score": 50, "passed": accuracy_score == 50, "reason": reason})

    # 4. 业务逻辑校验：展位分配与餐饮类型 (30分)
    # 抽样检查逻辑
    logic_score = 0
    if isinstance(data, list) and len(data) > 0:
        correct_logic_count = 0
        total_to_check = 0
        for item in data:
            name = item.get("Name")
            exhibit = item.get("Assigned_Exhibit")
            chow = item.get("Chow_Type")
            
            if name == "Little Bear": # 6岁 -> Potawatomi, Standard
                total_to_check += 1
                if exhibit == "Potawatomi_Crafts" and chow == "Standard MRE": correct_logic_count += 1
            elif name == "Alice Morningstar": # 12岁 -> Navajo, Standard
                total_to_check += 1
                if exhibit == "Navajo_Code_Talkers" and chow == "Standard MRE": correct_logic_count += 1
            elif name == "Cree Summer": # 17岁 -> Navajo, Special
                total_to_check += 1
                if exhibit == "Navajo_Code_Talkers" and chow == "Special Chow": correct_logic_count += 1
            elif name == "Billy Two-Hats": # 5岁, 'none' -> Potawatomi, Standard
                total_to_check += 1
                if exhibit == "Potawatomi_Crafts" and chow == "Standard MRE": correct_logic_count += 1
            elif name == "Sky Walker": # 10岁 -> Potawatomi, Special
                total_to_check += 1
                if exhibit == "Potawatomi_Crafts" and chow == "Special Chow": correct_logic_count += 1
        
        if total_to_check > 0:
            logic_score = (correct_logic_count / total_to_check) * 30
        
        score += int(logic_score)
        details.append({
            "item": "展位与饮食逻辑匹配度", 
            "score": int(logic_score), 
            "max_score": 30, 
            "passed": logic_score == 30, 
            "reason": f"逻辑匹配通过率: {correct_logic_count}/{total_to_check}"
        })

    write_score(score, details)

def write_score(score, details):
    output = {
        "total_score": int(score),
        "details": details
    }
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
