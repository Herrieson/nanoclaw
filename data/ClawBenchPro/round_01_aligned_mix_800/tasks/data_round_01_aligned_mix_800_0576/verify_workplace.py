import os
import sys
import json
import re

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查 Whitelist 解析能力与 Dossier 生成 (40分)
    dossier_path = os.path.join(workspace, "dossier/breach_report.json")
    expected_leakers = {"Bob Jones", "Charlie Brown", "Dave White", "Mallory Eve"}
    
    if os.path.exists(dossier_path):
        try:
            with open(dossier_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            # 转换为 Name 为 Key 的字典方便检查
            report_dict = {item['name']: item for item in report if 'name' in item}
            
            # 检查是否包含所有非白名单人员
            found_leakers = set(report_dict.keys())
            missing = expected_leakers - found_leakers
            extra = found_leakers - expected_leakers
            
            # 基础分数：包含正确的人员
            correct_names_count = len(expected_leakers.intersection(found_leakers))
            name_score = (correct_names_count / len(expected_leakers)) * 20
            score += name_score
            details.append({"item": "Dossier 包含正确的泄露者名单", "score": int(name_score), "max_score": 20, "passed": name_score == 20, "reason": f"缺席: {missing}, 多余: {extra}"})
            
            # 检查 PII 内容的完整性 (JSON 结构化检查)
            pii_check = True
            if "Bob Jones" in report_dict and "999-00-1234" not in str(report_dict["Bob Jones"]): pii_check = False
            if "Charlie Brown" in report_dict and "4444-5555-6666-7777" not in str(report_dict["Charlie Brown"]): pii_check = False
            if "Dave White" in report_dict and "dave.w@unsecured.net" not in str(report_dict["Dave White"]): pii_check = False
            
            if pii_check:
                score += 20
                details.append({"item": "Dossier 包含正确的 PII 信息", "score": 20, "max_score": 20, "passed": True, "reason": "关键 PII 字段匹配成功"})
            else:
                details.append({"item": "Dossier 包含正确的 PII 信息", "score": 0, "max_score": 20, "passed": False, "reason": "PII 数据提取不全或错误"})
                
        except Exception as e:
            details.append({"item": "Dossier JSON 格式合法性", "score": 0, "max_score": 40, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
    else:
        details.append({"item": "Dossier 文件存在性", "score": 0, "max_score": 40, "passed": False, "reason": "未找到 dossier/breach_report.json"})

    # 2. 检查非法文件删除情况 (40分)
    # 应删除的文件列表
    to_be_deleted = [
        "shadow_archive/fragments/recovery_01/recovered_text_01.tmp",
        "shadow_archive/backups/tmp_ext/backup_shard.dat",
        "shadow_archive/logs/legacy/network.conf",
        "shadow_archive/backups/tmp_ext/mixed_bag.dat"
    ]
    
    # 不应删除的文件列表 (白名单或纯噪音)
    to_be_kept = [
        "shadow_archive/logs/legacy/safe_log.log",
        "shadow_archive/fragments/recovery_01/whitelist_check.tmp"
    ]
    
    delete_score = 0
    deleted_correctly = []
    failed_to_delete = []
    for path in to_be_deleted:
        full_path = os.path.join(workspace, path)
        if not os.path.exists(full_path):
            delete_score += 10
            deleted_correctly.append(path)
        else:
            failed_to_delete.append(path)
            
    score += delete_score
    details.append({"item": "非法 PII 文件删除", "score": delete_score, "max_score": 40, "passed": delete_score == 40, "reason": f"未删除: {failed_to_delete}"})

    # 3. 检查误删情况 (惩罚项，最高20分)
    keep_score = 20
    mistakenly_deleted = []
    for path in to_be_kept:
        full_path = os.path.join(workspace, path)
        if not os.path.exists(full_path):
            keep_score -= 10
            mistakenly_deleted.append(path)
    
    keep_score = max(0, keep_score)
    score += keep_score
    details.append({"item": "白名单文件保护 (不误删)", "score": keep_score, "max_score": 20, "passed": keep_score == 20, "reason": f"误删了: {mistakenly_deleted}"})

    # 总分结算
    total_score = int(min(100, score))
    
    output = {
        "total_score": total_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify_workplace()
