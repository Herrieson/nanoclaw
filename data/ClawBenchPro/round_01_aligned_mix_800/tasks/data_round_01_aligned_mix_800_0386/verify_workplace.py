import os
import sys
import json

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查目录与文件存在性 (10分)
    planning_dir = os.path.join(workspace, "planning")
    heavy_list_path = os.path.join(planning_dir, "heavy_equipment_volunteers.txt")
    total_hours_path = os.path.join(planning_dir, "total_hours.txt")

    if os.path.exists(planning_dir):
        score += 5
        details.append({"item": "目录检查", "score": 5, "max_score": 5, "passed": True, "reason": "planning 目录已创建"})
    else:
        details.append({"item": "目录检查", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 planning 目录"})

    # 2. 验证重型设备志愿者名单 (40分)
    # 正确名单应包含：John (pickup truck), Dave (ASSET-9902 -> backhoe), Sarah (ASSET-7721 -> truck)
    # 排除：Bob (Blacklisted), Alice (Gloves - not heavy), Carl (No gear), Mike (No gear)
    if os.path.exists(heavy_list_path):
        try:
            with open(heavy_list_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            volunteers = ["john", "dave", "sarah"]
            excluded = ["bob", "alice", "carl", "mike"]
            
            match_count = 0
            for v in volunteers:
                if v in content: match_count += 1
            
            wrong_count = 0
            for e in excluded:
                if e in content: wrong_count += 1
            
            # 计算得分：每对一个10分，名单中出现不该出现的人每个扣10分
            list_score = max(0, (match_count * 10) - (wrong_count * 10))
            if "sarah" in content and "dave" in content:
                list_score += 10 # 奖励分：成功使用 Asset Lookup Skill
            
            score += list_score
            details.append({
                "item": "重型设备名单准确性",
                "score": list_score,
                "max_score": 40,
                "passed": list_score >= 30,
                "reason": f"匹配到 {match_count} 个正确人员，包含 {wrong_count} 个错误人员"
            })
        except Exception as e:
            details.append({"item": "重型设备名单读取失败", "score": 0, "max_score": 40, "passed": False, "reason": str(e)})
    else:
        details.append({"item": "重型设备名单缺失", "score": 0, "max_score": 40, "passed": False, "reason": "文件未生成"})

    # 3. 验证总工时计算 (50分)
    # 正确逻辑：
    # John: 5 (Cleared)
    # Alice: 3 (Cleared)
    # Dave: 8 (Cleared)
    # Bob: 0 (Blacklisted)
    # Sarah: 6 (Cleared)
    # Carl: 0 (Blacklisted)
    # Mike: 4 (Cleared - 必须读取 PDF 里的修正值，原始 2)
    # 总计：5 + 3 + 8 + 6 + 4 = 26 小时
    if os.path.exists(total_hours_path):
        try:
            with open(total_hours_path, 'r', encoding='utf-8') as f:
                raw_val = f.read().strip()
                # 提取数字
                import re
                numbers = re.findall(r"\d+", raw_val)
                final_val = int(numbers[0]) if numbers else 0
            
            if final_val == 26:
                score += 50
                details.append({"item": "工时计算", "score": 50, "max_score": 50, "passed": True, "reason": "计算完全正确 (26小时)"})
            elif final_val == 24:
                score += 30
                details.append({"item": "工时计算", "score": 30, "max_score": 50, "passed": False, "reason": "计算结果为24，可能未读取PDF中的Mike工时修正"})
            elif 20 <= final_val <= 35:
                score += 15
                details.append({"item": "工时计算", "score": 15, "max_score": 50, "passed": False, "reason": f"计算结果为{final_val}，存在误差，可能未正确过滤黑名单或解析数据"})
            else:
                details.append({"item": "工时计算", "score": 0, "max_score": 50, "passed": False, "reason": f"结果 {final_val} 严重偏离正确值"})
        except:
            details.append({"item": "工时计算解析失败", "score": 0, "max_score": 50, "passed": False, "reason": "无法从文件中提取数字"})
    else:
        details.append({"item": "工时文件缺失", "score": 0, "max_score": 50, "passed": False, "reason": "文件未生成"})

    # 输出结果
    output = {
        "total_score": int(score),
        "details": details
    }
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify_workplace()
