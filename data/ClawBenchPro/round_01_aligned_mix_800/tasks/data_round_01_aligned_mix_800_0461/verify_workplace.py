import os
import sys
import json
import csv
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = os.path.join(workspace, "clean_route")
    manifest_path = os.path.join(output_dir, "zone_7_manifest.json")
    deviations_path = os.path.join(output_dir, "deviations.txt")
    
    score = 0
    details = []

    # 1. 检查目录和文件是否存在 (10分)
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        score += 5
        details.append({"item": "目录 clean_route 存在", "score": 5, "max_score": 5, "passed": True, "reason": ""})
    else:
        details.append({"item": "目录 clean_route 存在", "score": 0, "max_score": 5, "passed": False, "reason": "未找到目录"})

    files_exist = os.path.exists(manifest_path) and os.path.exists(deviations_path)
    if files_exist:
        score += 5
        details.append({"item": "结果文件存在", "score": 5, "max_score": 5, "passed": True, "reason": ""})
    else:
        details.append({"item": "结果文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "缺失 zone_7_manifest.json 或 deviations.txt"})

    # 2. 验证 deviations.txt 内容 (30分)
    # 预期追踪号: TRK-9005 (Zone 9), TRK-3002 (Zone 3), TRK-9011 (Zone 9)
    expected_deviations = {"TRK-9005", "TRK-3002", "TRK-9011"}
    if os.path.exists(deviations_path):
        try:
            with open(deviations_path, "r") as f:
                content = [line.strip() for line in f if line.strip()]
            actual_deviations = set(content)
            
            if actual_deviations == expected_deviations:
                score += 30
                details.append({"item": "deviations.txt 内容准确性", "score": 30, "max_score": 30, "passed": True, "reason": "准确识别了所有 Zone 3/9 的追踪号"})
            elif expected_deviations.issubset(actual_deviations):
                score += 15
                details.append({"item": "deviations.txt 内容准确性", "score": 15, "max_score": 30, "passed": False, "reason": "包含了正确结果但混入了多余数据（可能未过滤 SYSTEM_VERIFIED）"})
            else:
                score += 5
                details.append({"item": "deviations.txt 内容准确性", "score": 5, "max_score": 30, "passed": False, "reason": f"匹配不全。预期: {expected_deviations}, 实际: {actual_deviations}"})
        except Exception as e:
            details.append({"item": "deviations.txt 内容准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"读取失败: {str(e)}"})
    else:
        details.append({"item": "deviations.txt 内容准确性", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})

    # 3. 验证 zone_7_manifest.json 内容与排序 (60分)
    # Zone 7 数据及 VIP 属性判定：
    # 1. TRK-7001 (Standard) -> Non-VIP
    # 2. TRK-7775 (Standard, but TRK-777 prefix) -> VIP
    # 3. TRK-8812 (RANK: VIP) -> VIP
    # 4. TRK-7009 (Normal) -> Non-VIP
    # 5. TRK-7110 (Level_1) -> VIP
    # 6. TRK-7012 (Priority) -> VIP
    
    expected_vips = {"TRK-7775", "TRK-8812", "TRK-7110", "TRK-7012"}
    expected_non_vips = {"TRK-7001", "TRK-7009"}
    all_zone_7 = expected_vips.union(expected_non_vips)

    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)
            
            actual_ids = []
            if isinstance(data, list):
                # 兼容不同字段名提取
                for item in data:
                    tid = item.get("tracking") or item.get("tracking_no") or item.get("PACKAGE_ID")
                    if tid: actual_ids.append(tid)
            
            # 3.1 集合完整性 (30分)
            if set(actual_ids) == all_zone_7:
                score += 30
                details.append({"item": "Zone 7 数据提取完整性", "score": 30, "max_score": 30, "passed": True, "reason": "成功提取了所有 verified 且属于 Zone 7 的数据"})
            else:
                missing = all_zone_7 - set(actual_ids)
                extra = set(actual_ids) - all_zone_7
                score += max(0, 30 - len(missing)*10 - len(extra)*10)
                details.append({"item": "Zone 7 数据提取完整性", "score": max(0, 30 - len(missing)*10 - len(extra)*10), "max_score": 30, "passed": False, "reason": f"缺失: {missing}, 多余: {extra}"})

            # 3.2 VIP 排序逻辑 (30分)
            # VIP 必须在最上方。检查前 4 个是否都在 expected_vips 中
            if len(actual_ids) >= 4:
                top_4 = set(actual_ids[:4])
                if top_4 == expected_vips:
                    score += 30
                    details.append({"item": "VIP 排序逻辑", "score": 30, "max_score": 30, "passed": True, "reason": "VIP 追踪号已正确置顶"})
                else:
                    score += 10
                    details.append({"item": "VIP 排序逻辑", "score": 10, "max_score": 30, "passed": False, "reason": f"VIP 排序不正确。列表顶端应为 VIP，实际前四个为: {top_4}"})
            else:
                details.append({"item": "VIP 排序逻辑", "score": 0, "max_score": 30, "passed": False, "reason": "数据量不足以判定排序"})

        except Exception as e:
            details.append({"item": "zone_7_manifest.json 格式验证", "score": 0, "max_score": 60, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
    else:
        details.append({"item": "zone_7_manifest.json 格式验证", "score": 0, "max_score": 60, "passed": False, "reason": "文件不存在"})

    # 4. 严查幻觉：是否混入了 SYSTEM_VERIFIED: FALSE 的 TRK-7999 (扣分项)
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            if "TRK-7999" in f.read():
                score = max(0, score - 20)
                details.append({"item": "反幻觉检查", "score": -20, "max_score": 0, "passed": False, "reason": "错误包含了未验证(FALSE)的数据 TRK-7999"})

    # 输出结果
    result = {
        "total_score": max(0, min(100, int(score))),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
