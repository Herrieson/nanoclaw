import os
import sys
import json

def verify_workplace(workspace_dir):
    score_details = []
    total_score = 0

    # Expected Ground Truth
    expected_trespassers = {"Darius Vance", "Chloe Baxter", "Jaxson Cole", "Luna Sterling", "Silas Vance"}
    decoy_trespassers = {"Ghost_Trespasser_Past", "Ghost_Trespasser_Future"}
    
    expected_missing_vinyls = {
        "V-002": {"title": "Nina Simone - Pastel Blues", "borrower": "Darius Vance"},
        "V-004": {"title": "Miles Davis - Kind of Blue", "borrower": "Chloe Baxter"},
        "V-088": {"title": "Thelonious Monk - Genius of Modern Music", "borrower": "Student_42"},
        "V-102": {"title": "Bill Evans - Waltz for Debby", "borrower": "Dr. Faculty_12"},
        "V-105": {"title": "Chet Baker - Chet Baker Sings", "borrower": "Luna Sterling"}
    }

    # 1. 检查 trespassers.txt 存在性
    trespassers_path = os.path.join(workspace_dir, "investigation", "trespassers.txt")
    if os.path.isfile(trespassers_path):
        score_details.append({"item": "trespassers.txt文件存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件已创建"})
        total_score += 5
        
        with open(trespassers_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            agent_trespassers = set(lines)
        
        # 检查是否包含正确的闯入者
        correct_count = len(expected_trespassers.intersection(agent_trespassers))
        pts = correct_count * 5
        total_score += pts
        score_details.append({"item": "正确找出10月24日的闯入者", "score": pts, "max_score": 25, "passed": pts == 25, "reason": f"找到 {correct_count}/5 个正确的闯入者"})

        # 检查是否过滤了Decoy
        has_decoys = len(decoy_trespassers.intersection(agent_trespassers)) > 0
        if not has_decoys:
            total_score += 10
            score_details.append({"item": "成功过滤非24日的虚假闯入者", "score": 10, "max_score": 10, "passed": True, "reason": "未包含非指定日期的记录"})
        else:
            score_details.append({"item": "成功过滤非24日的虚假闯入者", "score": 0, "max_score": 10, "passed": False, "reason": "包含了23日或25日的记录"})
            
        # 检查是否有多余的人员
        extra_people = agent_trespassers - expected_trespassers - decoy_trespassers
        if len(extra_people) == 0:
            total_score += 5
            score_details.append({"item": "无其他误报名单", "score": 5, "max_score": 5, "passed": True, "reason": "未包含无关人员"})
        else:
            score_details.append({"item": "无其他误报名单", "score": 0, "max_score": 5, "passed": False, "reason": f"存在误报人员数量: {len(extra_people)}"})

    else:
        score_details.append({"item": "trespassers.txt文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件未创建"})
        score_details.append({"item": "正确找出10月24日的闯入者", "score": 0, "max_score": 25, "passed": False, "reason": "文件缺失"})
        score_details.append({"item": "成功过滤非24日的虚假闯入者", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        score_details.append({"item": "无其他误报名单", "score": 0, "max_score": 5, "passed": False, "reason": "文件缺失"})

    # 2. 检查 missing_vinyls.json 存在与格式
    missing_json_path = os.path.join(workspace_dir, "investigation", "missing_vinyls.json")
    if os.path.isfile(missing_json_path):
        score_details.append({"item": "missing_vinyls.json文件存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件已创建"})
        total_score += 5
        
        try:
            with open(missing_json_path, "r", encoding="utf-8") as f:
                missing_data = json.load(f)
            
            if isinstance(missing_data, list):
                score_details.append({"item": "JSON格式为有效列表", "score": 5, "max_score": 5, "passed": True, "reason": "最外层是Array"})
                total_score += 5
                
                # 检查提取的数据正确性
                agent_records = {}
                for item in missing_data:
                    rid = item.get("record_id")
                    if rid:
                        agent_records[rid] = item

                matched_records = 0
                for exp_rid, exp_info in expected_missing_vinyls.items():
                    if exp_rid in agent_records:
                        agent_record = agent_records[exp_rid]
                        if agent_record.get("title") == exp_info["title"] and agent_record.get("borrower") == exp_info["borrower"]:
                            matched_records += 1
                
                pts_records = matched_records * 6
                total_score += pts_records
                score_details.append({"item": "准确提取丢失唱片的ID、Title和Borrower", "score": pts_records, "max_score": 30, "passed": pts_records == 30, "reason": f"精确匹配 {matched_records}/5 个丢失记录"})
                
                # 检查是否有捏造的记录
                extra_records = set(agent_records.keys()) - set(expected_missing_vinyls.keys())
                if len(extra_records) == 0:
                    total_score += 15
                    score_details.append({"item": "无错误提取已归还唱片", "score": 15, "max_score": 15, "passed": True, "reason": "仅包含未归还的记录，剔除了已归还的噪音"})
                else:
                    score_details.append({"item": "无错误提取已归还唱片", "score": 0, "max_score": 15, "passed": False, "reason": f"误判了 {len(extra_records)} 个已归还唱片为丢失"})

            else:
                score_details.append({"item": "JSON格式为有效列表", "score": 0, "max_score": 5, "passed": False, "reason": "JSON根节点不是List"})
                score_details.append({"item": "准确提取丢失唱片的ID、Title和Borrower", "score": 0, "max_score": 30, "passed": False, "reason": "格式错误无法验证"})
                score_details.append({"item": "无错误提取已归还唱片", "score": 0, "max_score": 15, "passed": False, "reason": "格式错误无法验证"})
                
        except json.JSONDecodeError:
            score_details.append({"item": "JSON格式为有效列表", "score": 0, "max_score": 5, "passed": False, "reason": "文件包含非法的JSON格式"})
            score_details.append({"item": "准确提取丢失唱片的ID、Title和Borrower", "score": 0, "max_score": 30, "passed": False, "reason": "解析失败"})
            score_details.append({"item": "无错误提取已归还唱片", "score": 0, "max_score": 15, "passed": False, "reason": "解析失败"})

    else:
        score_details.append({"item": "missing_vinyls.json文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件未创建"})
        score_details.append({"item": "JSON格式为有效列表", "score": 0, "max_score": 5, "passed": False, "reason": "文件缺失"})
        score_details.append({"item": "准确提取丢失唱片的ID、Title和Borrower", "score": 0, "max_score": 30, "passed": False, "reason": "文件缺失"})
        score_details.append({"item": "无错误提取已归还唱片", "score": 0, "max_score": 15, "passed": False, "reason": "文件缺失"})

    # Output results
    with open(os.path.join(workspace_dir, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
