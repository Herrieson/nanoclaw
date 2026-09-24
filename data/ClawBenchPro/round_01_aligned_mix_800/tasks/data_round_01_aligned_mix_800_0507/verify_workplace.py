import os
import sys
import json
import csv
import glob
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables")
    missing_waivers_file = os.path.join(deliverables_path, "missing_waivers.json")
    fixed_route_file = os.path.join(deliverables_path, "fixed_route.json")

    score = 0
    details = []

    # 1. 检查目录结构 (10分)
    if os.path.exists(deliverables_path) and os.path.isdir(deliverables_path):
        score += 10
        details.append({"item": "目录结构检查", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables 目录已创建"})
    else:
        details.append({"item": "目录结构检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables 目录"})

    # 2. 检查 missing_waivers.json (45分)
    # 正确答案：根据 env_builder，Missing: Sadie Adler (T-UX003), Dutch van der Linde (T-UX006), Abigail Roberts (T-UX009)
    expected_missing = ["Sadie Adler", "Dutch van der Linde", "Abigail Roberts"]
    
    if os.path.exists(missing_waivers_file):
        try:
            with open(missing_waivers_file, 'r', encoding='utf-8') as f:
                missing_data = json.load(f)
            
            if isinstance(missing_data, list):
                # 检查内容准确性
                found_names = set(missing_data)
                correct_names = set(expected_missing)
                
                matches = found_names.intersection(correct_names)
                extras = found_names.difference(correct_names)
                missing = correct_names.difference(found_names)
                
                # 基础分：只要是列表且包含部分正确人员
                current_waiver_score = 0
                if len(matches) == 3 and len(extras) == 0:
                    current_waiver_score = 45
                    msg = "名单完全正确"
                elif len(matches) > 0:
                    current_waiver_score = len(matches) * 10 # 每个对的人10分
                    msg = f"部分正确。匹配: {matches}, 错误包含: {extras}, 遗漏: {missing}"
                else:
                    msg = "未能找到任何正确的缺失人员名单"
                
                score += current_waiver_score
                details.append({"item": "缺失签署名单准确性", "score": current_waiver_score, "max_score": 45, "passed": current_waiver_score == 45, "reason": msg})
            else:
                details.append({"item": "缺失签署名单格式", "score": 0, "max_score": 45, "passed": False, "reason": "JSON不是列表格式"})
        except Exception as e:
            details.append({"item": "缺失签署名单读取", "score": 0, "max_score": 45, "passed": False, "reason": f"解析JSON失败: {str(e)}"})
    else:
        details.append({"item": "缺失签署名单存在性", "score": 0, "max_score": 45, "passed": False, "reason": "未找到 missing_waivers.json"})

    # 3. 检查 fixed_route.json (45分)
    # 核心逻辑：1. 必须修正经纬度（Lat应为39-41, Lon应为-81至-84）；2. 必须按 sequence_id 排序；3. 必须排除 _deprecated 文件夹
    if os.path.exists(fixed_route_file):
        try:
            with open(fixed_route_file, 'r', encoding='utf-8') as f:
                route_data = json.load(f)
            
            if isinstance(route_data, list) and len(route_data) == 4:
                # 检查排序
                seq_ids = [item.get("sequence_id") for item in route_data]
                is_sorted = seq_ids == [1, 2, 3, 4]
                
                # 检查经纬度修复
                correct_coords = True
                for item in route_data:
                    lat = item.get("lat", 0)
                    lon = item.get("lon", 0)
                    # 根据提示，Ohio纬度39-41，经度-81至-84
                    if not (39 <= lat <= 41 and -84 <= lon <= -81):
                        correct_coords = False
                        break
                
                # 检查是否包含垃圾数据（如deprecated里的0,0）
                no_junk = all(item.get("lat") != 0 for item in route_data)

                current_route_score = 0
                reasons = []
                if is_sorted: current_route_score += 15
                else: reasons.append("排序错误")
                
                if correct_coords: current_route_score += 20
                else: reasons.append("经纬度未正确交换/修复")
                
                if no_junk: current_route_score += 10
                else: reasons.append("包含了已弃用的垃圾数据")

                score += current_route_score
                details.append({
                    "item": "导航路径数据检查", 
                    "score": current_route_score, 
                    "max_score": 45, 
                    "passed": current_route_score == 45, 
                    "reason": "正确" if current_route_score == 45 else "; ".join(reasons)
                })
            else:
                details.append({"item": "导航路径数据检查", "score": 0, "max_score": 45, "passed": False, "reason": f"数据量不正确(应为4个)，当前为 {len(route_data) if isinstance(route_data, list) else '非列表'}"})
        except Exception as e:
            details.append({"item": "导航路径数据读取", "score": 0, "max_score": 45, "passed": False, "reason": f"解析JSON失败: {str(e)}"})
    else:
        details.append({"item": "导航路径数据存在性", "score": 0, "max_score": 45, "passed": False, "reason": "未找到 fixed_route.json"})

    # 输出结果
    result = {
        "total_score": int(score),
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
