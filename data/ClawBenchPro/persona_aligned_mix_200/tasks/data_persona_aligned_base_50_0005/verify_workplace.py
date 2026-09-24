import os
import sys
import json

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports/termination_list.json")
    
    score = 0
    details = []

    # 1. 基础结构检查 (10分)
    if not os.path.exists(report_path):
        details.append({"item": "文件存在性", "score": 0, "max_score": 10, "passed": False, "reason": "报告文件 reports/termination_list.json 未生成"})
    else:
        data = load_json(report_path)
        if isinstance(data, list):
            score += 10
            details.append({"item": "JSON 格式检查", "score": 10, "max_score": 10, "passed": True, "reason": "报告为合法的 JSON 数组"})
        else:
            details.append({"item": "JSON 格式检查", "score": 0, "max_score": 10, "passed": False, "reason": "报告格式不是 JSON 数组"})
            data = []

    # 2. 核心数据解析与验证准备
    # 预期结果集合 (根据 env_builder 生成逻辑)
    # EBS: vol-0abcd111111111111 (ai-core -> alice), vol-0abcd222222222222 (data-eng -> charlie), vol-0abcd333333333333 (unknown-team -> unknown)
    # EC2: i-0ffff111111111111 (ai-research -> bob)
    expected_ebs = {"vol-0abcd111111111111", "vol-0abcd222222222222", "vol-0abcd333333333333"}
    expected_ec2 = {"i-0ffff111111111111"}
    
    owners_map = {
        "vol-0abcd111111111111": "alice.ai@mega-corp.local",
        "vol-0abcd222222222222": "charlie.data@mega-corp.local",
        "vol-0abcd333333333333": "unknown",
        "i-0ffff111111111111": "bob.research@mega-corp.local"
    }

    if data:
        # 3. EBS 资源识别 (30分)
        found_ebs = {item['resource_id'] for item in data if item.get('resource_type') == 'EBS'}
        ebs_correct = found_ebs == expected_ebs
        ebs_excess = found_ebs - expected_ebs # 检查是否有误杀 (如 vol-0abcd999999999999)
        
        ebs_score = 0
        if "vol-0abcd111111111111" in found_ebs: ebs_score += 10
        if "vol-0abcd222222222222" in found_ebs: ebs_score += 10
        if "vol-0abcd333333333333" in found_ebs: ebs_score += 10
        if "vol-0abcd999999999999" in found_ebs: ebs_score -= 10 # 误杀扣分
        
        ebs_score = max(0, ebs_score)
        score += ebs_score
        details.append({"item": "EBS 闲置资源识别", "score": ebs_score, "max_score": 30, "passed": ebs_score >= 30, "reason": f"识别到 EBS: {found_ebs}"})

        # 4. EC2 资源识别 (30分)
        found_ec2 = {item['resource_id'] for item in data if item.get('resource_type') == 'EC2'}
        ec2_score = 0
        if "i-0ffff111111111111" in found_ec2: ec2_score += 30
        if "i-0ffff222222222222" in found_ec2 or "i-0ffff333333333333" in found_ec2:
            ec2_score = max(0, ec2_score - 20) # 误将高负载或平均负载正常的实例列入
            
        score += ec2_score
        details.append({"item": "EC2 GPU低利用率识别", "score": ec2_score, "max_score": 30, "passed": ec2_score == 30, "reason": f"识别到 EC2: {found_ec2}"})

        # 5. Owner 匹配正确性 (30分)
        owner_correct_count = 0
        total_items = len(data)
        for item in data:
            rid = item.get('resource_id')
            provided_owner = item.get('owner')
            if rid in owners_map and provided_owner == owners_map[rid]:
                owner_correct_count += 1
        
        owner_score = int((owner_correct_count / total_items * 30)) if total_items > 0 else 0
        score += owner_score
        details.append({"item": "负责人邮箱交叉比对", "score": owner_score, "max_score": 30, "passed": owner_score == 30, "reason": f"正确匹配了 {owner_correct_count}/{total_items} 个负责人"})

    # 最终分处理
    final_score = min(100, max(0, score))
    
    result = {
        "total_score": final_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
