import os
import sys
import json

def verify():
    # 基础路径处理
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports/bottleneck.json")
    
    score = 0
    details = []

    # 1. 检查结果文件是否存在 (10分)
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "Check reports/bottleneck.json existence", "score": 10, "max_score": 10, "passed": True, "reason": "Report file found."})
    else:
        details.append({"item": "Check reports/bottleneck.json existence", "score": 0, "max_score": 10, "passed": False, "reason": "Report file not found."})
        # 如果文件不存在，后续检查无法进行，直接写入结果
        write_score(score, details)
        return

    # 2. 检查 JSON 格式与 Schema 合法性 (20分)
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "bottleneck_entity" in data:
            score += 20
            details.append({"item": "Verify JSON Schema", "score": 20, "max_score": 20, "passed": True, "reason": "Key 'bottleneck_entity' exists."})
            
            # 3. 检查 Entity ID 准确性 (70分)
            # 根据 env_builder.py, target_entity = "8847291"
            actual_id = str(data["bottleneck_entity"]).strip()
            expected_id = "8847291"
            
            if actual_id == expected_id:
                score += 70
                details.append({"item": "Verify Bottleneck Entity ID", "score": 70, "max_score": 70, "passed": True, "reason": f"Correct entity ID found: {actual_id}"})
            else:
                details.append({"item": "Verify Bottleneck Entity ID", "score": 0, "max_score": 70, "passed": False, "reason": f"Incorrect entity ID. Expected {expected_id}, but got {actual_id}"})
        
        else:
            details.append({"item": "Verify JSON Schema", "score": 0, "max_score": 20, "passed": False, "reason": "Required key 'bottleneck_entity' is missing."})

    except json.JSONDecodeError:
        details.append({"item": "Verify JSON Schema", "score": 0, "max_score": 20, "passed": False, "reason": "File is not a valid JSON."})
    except Exception as e:
        details.append({"item": "Verify JSON Schema", "score": 0, "max_score": 20, "passed": False, "reason": f"Unexpected error: {str(e)}"})

    write_score(score, details)

def write_score(total_score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
