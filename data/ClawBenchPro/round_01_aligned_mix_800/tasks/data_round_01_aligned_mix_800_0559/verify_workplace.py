import os
import sys
import json
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    deliverables_dir = os.path.join(workspace, "deliverables")
    crm_file = os.path.join(deliverables_dir, "ready_for_crm.json")
    volunteer_file = os.path.join(deliverables_dir, "volunteer_contacts.txt")
    
    # 1. 检查 deliverables 目录
    if os.path.isdir(deliverables_dir):
        score_details.append({"item": "目录 deliverables 存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建 deliverables 目录"})
        total_score += 10
    else:
        score_details.append({"item": "目录 deliverables 存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables 目录"})
        
    # 2. 检查 ready_for_crm.json (满分 45)
    if os.path.isfile(crm_file):
        try:
            with open(crm_file, "r", encoding="utf-8") as f:
                crm_data = json.load(f)
            
            if not isinstance(crm_data, list):
                score_details.append({"item": "CRM 数据格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "ready_for_crm.json 必须是 JSON 数组"})
            else:
                score_details.append({"item": "CRM 数据格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "ready_for_crm.json 解析为 JSON 数组"})
                total_score += 10
                
                # 检查内容正确性
                expected_crm_companies = {"Quantum Fiber East", "South Star Logistics", "East Coast Bakery"}
                extracted_companies = set([item.get("Company_Name", "") for item in crm_data])
                
                # 检查是否包含正确的公司 (15分)
                correct_count = len(expected_crm_companies.intersection(extracted_companies))
                crm_match_score = correct_count * 5
                total_score += crm_match_score
                score_details.append({
                    "item": "CRM 目标公司精准提取", 
                    "score": crm_match_score, 
                    "max_score": 15, 
                    "passed": crm_match_score == 15, 
                    "reason": f"提取到 {correct_count}/3 个目标公司"
                })
                
                # 检查是否混入了噪音数据和不合格电话 (20分)
                invalid_data = False
                for item in crm_data:
                    phone = item.get("Phone", "")
                    # 如果有非10位数字或者混入了不需要的区/假公司，判定为过滤失败
                    if not (phone.isdigit() and len(phone) == 10) or "FakeBiz" in item.get("Company_Name", ""):
                        invalid_data = True
                        break
                
                if invalid_data:
                    score_details.append({"item": "CRM 严格过滤噪音与无效数据", "score": 0, "max_score": 20, "passed": False, "reason": "混入了无效电话或干扰数据"})
                else:
                    if len(crm_data) == 3 and correct_count == 3:
                        score_details.append({"item": "CRM 严格过滤噪音与无效数据", "score": 20, "max_score": 20, "passed": True, "reason": "完美剔除了所有噪音数据且符合长度及纯数字要求"})
                        total_score += 20
                    else:
                        score_details.append({"item": "CRM 严格过滤噪音与无效数据", "score": 10, "max_score": 20, "passed": False, "reason": "无明显脏数据，但条目总数不完全匹配期望值"})
                        total_score += 10
                        
        except json.JSONDecodeError:
            score_details.append({"item": "CRM 数据格式合法", "score": 0, "max_score": 45, "passed": False, "reason": "ready_for_crm.json 无法被 JSON 解析"})
    else:
        score_details.append({"item": "CRM 数据文件存在", "score": 0, "max_score": 45, "passed": False, "reason": "未生成 ready_for_crm.json"})

    # 3. 检查 volunteer_contacts.txt (满分 45)
    if os.path.isfile(volunteer_file):
        try:
            with open(volunteer_file, "r", encoding="utf-8") as f:
                vol_text = f.read()
                
            score_details.append({"item": "志愿者名单文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "volunteer_contacts.txt 文件已生成"})
            total_score += 10
            
            # 必须包含名字和Email
            expected_vol_targets = ["Charity First", "love@charity.org", "Unity Hub", "admin@unity.org"]
            found_count = 0
            for target in expected_vol_targets:
                if target in vol_text:
                    found_count += 1
                    
            vol_match_score = int((found_count / 4) * 20)
            total_score += vol_match_score
            score_details.append({
                "item": "志愿者信息精准提取", 
                "score": vol_match_score, 
                "max_score": 20, 
                "passed": vol_match_score == 20, 
                "reason": f"提取到 {found_count}/4 个关键志愿者字段 (机构名与邮箱)"
            })
            
            # 检查是否混入 FakeBiz 或其他错误类型
            if "FakeBiz" in vol_text or "Quantum" in vol_text or "South Star" in vol_text:
                score_details.append({"item": "志愿者名单纯净度校验", "score": 0, "max_score": 15, "passed": False, "reason": "名单中混入了非志愿者数据 (干扰企业或测试数据)"})
            else:
                score_details.append({"item": "志愿者名单纯净度校验", "score": 15, "max_score": 15, "passed": True, "reason": "名单纯净，无干扰杂项"})
                total_score += 15
                
        except Exception as e:
            score_details.append({"item": "志愿者名单解析", "score": 0, "max_score": 45, "passed": False, "reason": f"读取文件出错: {e}"})
    else:
        score_details.append({"item": "志愿者数据文件存在", "score": 0, "max_score": 45, "passed": False, "reason": "未生成 volunteer_contacts.txt"})

    # 输出结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(f"Verify completed. Total Score: {total_score}")

if __name__ == "__main__":
    verify()
