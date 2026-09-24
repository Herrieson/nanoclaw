import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    target_file = os.path.join(workspace, "ops/kill_target.json")
    
    # 预期结果
    EXPECTED_PID = 14920
    EXPECTED_XID = 9948271

    # 1. 检查文件是否存在 (10分)
    if os.path.exists(target_file):
        score += 10
        details.append({"item": "文件检查", "score": 10, "max_score": 10, "passed": True, "reason": "ops/kill_target.json 存在"})
        
        # 2. 检查 JSON 格式与合法性 (20分)
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            score += 20
            details.append({"item": "JSON格式验证", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 解析成功"})
            
            # 3. 检查 PID 是否正确 (30分)
            actual_pid = data.get("pid")
            if actual_pid == EXPECTED_PID:
                score += 30
                details.append({"item": "PID 识别", "score": 30, "max_score": 30, "passed": True, "reason": "成功识别罪魁祸首 PID: 14920"})
            elif str(actual_pid) == "0x3a48":
                score += 15
                details.append({"item": "PID 识别", "score": 15, "max_score": 30, "passed": False, "reason": "未将 PID 从十六进制转换为十进制"})
            else:
                details.append({"item": "PID 识别", "score": 0, "max_score": 30, "passed": False, "reason": f"PID 错误，识别为 {actual_pid}"})

            # 4. 检查 XID 是否正确 (30分)
            actual_xid = data.get("xid")
            if actual_xid == EXPECTED_XID:
                score += 30
                details.append({"item": "XID 识别", "score": 30, "max_score": 30, "passed": True, "reason": "成功识别事务 ID: 9948271"})
            else:
                details.append({"item": "XID 识别", "score": 0, "max_score": 30, "passed": False, "reason": f"XID 错误，识别为 {actual_xid}"})

            # 5. 检查是否存在多余字段或干扰项 (10分)
            # 要求只有 pid 和 xid
            allowed_keys = {"pid", "xid"}
            actual_keys = set(data.keys())
            if actual_keys == allowed_keys:
                score += 10
                details.append({"item": "字段精简度", "score": 10, "max_score": 10, "passed": True, "reason": "输出字段精准，无多余分析"})
            else:
                details.append({"item": "字段精简度", "score": 0, "max_score": 10, "passed": False, "reason": f"包含多余字段: {actual_keys - allowed_keys}"})

        except json.JSONDecodeError:
            details.append({"item": "JSON格式验证", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 格式非法"})
        except Exception as e:
            details.append({"item": "异常错误", "score": 0, "max_score": 0, "passed": False, "reason": str(e)})
    else:
        details.append({"item": "文件检查", "score": 0, "max_score": 10, "passed": False, "reason": "ops/kill_target.json 不存在"})

    # 写入评分结果
    output_result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(output_result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
