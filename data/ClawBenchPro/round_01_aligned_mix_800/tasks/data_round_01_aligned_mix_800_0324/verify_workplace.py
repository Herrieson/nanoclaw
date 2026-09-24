import os
import sys
import json
import glob

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results_dir = os.path.join(workspace, "results")
    
    score_details = []
    total_score = 0
    
    # 1. Check if results directory exists
    if os.path.isdir(results_dir):
        score_details.append({"item": "检查 results 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "results 目录已创建"})
        total_score += 10
    else:
        score_details.append({"item": "检查 results 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 results 目录"})
        return write_score(total_score, score_details, workspace)

    # 2. Find and parse JSON file
    json_files = glob.glob(os.path.join(results_dir, "*.json"))
    report_data = None
    if json_files:
        try:
            with open(json_files[0], 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            score_details.append({"item": "检查报告格式是否为合法 JSON", "score": 20, "max_score": 20, "passed": True, "reason": "成功解析 JSON 文件"})
            total_score += 20
        except json.JSONDecodeError:
            score_details.append({"item": "检查报告格式是否为合法 JSON", "score": 0, "max_score": 20, "passed": False, "reason": "文件内容不是合法的 JSON"})
    else:
        # Try to parse any file in results just in case they didn't use .json extension
        all_files = os.listdir(results_dir)
        for fname in all_files:
            fpath = os.path.join(results_dir, fname)
            if os.path.isfile(fpath):
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                    score_details.append({"item": "检查报告格式是否为合法 JSON", "score": 20, "max_score": 20, "passed": True, "reason": "成功解析未带后缀的 JSON 文件"})
                    total_score += 20
                    break
                except:
                    continue
        if report_data is None:
            score_details.append({"item": "检查报告格式是否为合法 JSON", "score": 0, "max_score": 20, "passed": False, "reason": "results 目录下未找到合法的 JSON 文件"})

    if not report_data:
        return write_score(total_score, score_details, workspace)

    # 3. Check unauthorized members
    # Flatten all string values and list items in the JSON to find the members
    report_str = json.dumps(report_data).lower()
    has_frank = "frank miller" in report_str
    has_grace = "grace kelly" in report_str
    has_alice = "alice henderson" in report_str
    has_bob = "bob jenkins" in report_str
    
    unauth_score = 0
    unauth_reason = []
    if has_frank and has_grace:
        unauth_score += 30
        unauth_reason.append("成功识别出 Frank Miller 和 Grace Kelly")
        if not has_alice and not has_bob:
            unauth_score += 10
            unauth_reason.append("未包含合法的志愿者，无幻觉/误报")
        else:
            unauth_reason.append("错误地包含了合法的志愿者，扣10分")
    else:
        if has_frank or has_grace:
            unauth_score += 15
            unauth_reason.append("仅部分识别出违规志愿者")
        else:
            unauth_reason.append("未能识别出违规志愿者")
    
    score_details.append({
        "item": "验证违规志愿者名单", 
        "score": unauth_score, 
        "max_score": 40, 
        "passed": unauth_score == 40, 
        "reason": "；".join(unauth_reason)
    })
    total_score += unauth_score

    # 4. Check Heritage calculation
    # The expected sum is 43.75
    # We will search for this exact number in the JSON structure
    calc_score = 0
    calc_reason = ""
    def find_number(data, target):
        if isinstance(data, (int, float)):
            return abs(data - target) < 0.001
        elif isinstance(data, str):
            return str(target) in data
        elif isinstance(data, dict):
            return any(find_number(v, target) for v in data.values())
        elif isinstance(data, list):
            return any(find_number(v, target) for v in data)
        return False

    if find_number(report_data, 43.75):
        calc_score = 30
        calc_reason = "精确计算出 Heritage 分类的总销售额为 43.75"
    elif find_number(report_data, 51.25):
        calc_score = 0
        calc_reason = "错误地将所有类别的销售额相加 (51.25)"
    else:
        calc_score = 0
        calc_reason = "未能找到正确的 Heritage 总销售额 (43.75)"
        
    score_details.append({
        "item": "验证 Heritage 销售额计算", 
        "score": calc_score, 
        "max_score": 30, 
        "passed": calc_score == 30, 
        "reason": calc_reason
    })
    total_score += calc_score

    write_score(total_score, score_details, workspace)

def write_score(total_score, details, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Verification complete. Total Score: {total_score}")

if __name__ == "__main__":
    verify()
