import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score = 0
    details = []
    
    # 1. 检查目录结构与文件归类 (20分)
    solar_dir = os.path.join(workspace, "organized", "solar_logs")
    water_dir = os.path.join(workspace, "organized", "water_logs")
    
    solar_files_expected = {"solar_january.solx", "solar_february.solx"}
    water_files_expected = {"water_sensor_front.json", "water_sensor_back.json"}
    
    dir_score = 0
    if os.path.exists(solar_dir) and os.path.exists(water_dir):
        dir_score += 10
        
        solar_files_actual = set(os.listdir(solar_dir))
        water_files_actual = set(os.listdir(water_dir))
        
        if solar_files_actual == solar_files_expected:
            dir_score += 5
        if water_files_actual == water_files_expected:
            dir_score += 5
            
    details.append({
        "item": "检查文件整理目录是否存在及日志文件归类是否完全精准", 
        "score": dir_score, 
        "max_score": 20, 
        "passed": dir_score == 20, 
        "reason": "检查 organized/solar_logs 和 organized/water_logs 是否存在且仅包含对应的目标文件"
    })
    score += dir_score
    
    # 2. 检查无关噪音文件是否被正确过滤 (10分)
    noise_score = 0
    dumps_dir = os.path.join(workspace, "gadget_dumps")
    receipt_path = os.path.join(dumps_dir, "grocery_receipt.txt")
    news_path = os.path.join(dumps_dir, "tech_news_article.txt")
    if os.path.exists(receipt_path) and os.path.exists(news_path):
        noise_score = 10
    details.append({
        "item": "检查无关噪音文件是否被正确忽略且未被误删/误移", 
        "score": noise_score, 
        "max_score": 10, 
        "passed": noise_score == 10, 
        "reason": "噪音文件 grocery_receipt.txt 与 tech_news_article.txt 应保留在原处"
    })
    score += noise_score

    # 3. 检查最终目标结果文件是否存在及其 Schema 合法性 (20分)
    json_path = os.path.join(workspace, "smart_display_feed.json")
    if not os.path.exists(json_path):
        details.append({"item": "检查目标 JSON 文件是否存在及 Schema 合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"未找到文件 {json_path}"})
        details.append({"item": "严格校验总额计算的准确性", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在，无法校验"})
        details.append({"item": "校验生态指数评分是否存在且合规", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在，无法校验"})
    else:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            format_score = 20
            # 严格 Schema 检查：只能有指定的 3 个键，禁止捏造其它字段
            expected_keys = {"total_solar_kwh", "total_water_gallons", "eco_impact_score"}
            actual_keys = set(data.keys())
            if actual_keys != expected_keys:
                format_score = 0
                details.append({
                    "item": "检查目标 JSON 文件是否存在及 Schema 合法性", 
                    "score": format_score, 
                    "max_score": 20, 
                    "passed": False, 
                    "reason": f"Schema校验失败！文件包含多余或缺失的字段: {actual_keys}"
                })
            else:
                details.append({
                    "item": "检查目标 JSON 文件是否存在及 Schema 合法性", 
                    "score": format_score, 
                    "max_score": 20, 
                    "passed": True, 
                    "reason": "文件存在且 Schema 字段严格匹配"
                })
            score += format_score
            
            # 4. 严格校验总额计算的准确性 (30分)
            value_score = 0
            if data.get("total_solar_kwh") == 100:
                value_score += 15
            if data.get("total_water_gallons") == 200:
                value_score += 15
            details.append({
                "item": "严格校验总额计算的准确性", 
                "score": value_score, 
                "max_score": 30, 
                "passed": value_score == 30, 
                "reason": f"解析得到 total_solar_kwh={data.get('total_solar_kwh')}, total_water_gallons={data.get('total_water_gallons')} (应为 100 和 200)"
            })
            score += value_score
            
            # 5. 校验生态指数评分是否存在且类型合规 (20分)
            eco_score = 0
            eco_val = data.get("eco_impact_score")
            # 必须为整数且来源于 Mock API
            if isinstance(eco_val, int) and eco_val > 0:
                eco_score = 20
            details.append({
                "item": "校验生态指数评分是否存在且合规", 
                "score": eco_score, 
                "max_score": 20, 
                "passed": eco_score == 20, 
                "reason": f"eco_impact_score 值为 {eco_val}，且为合法的整数"
            })
            score += eco_score
            
        except json.JSONDecodeError:
            details.append({"item": "检查目标 JSON 文件是否存在及 Schema 合法性", "score": 0, "max_score": 20, "passed": False, "reason": "文件并非合法的 JSON 格式，无法解析"})
            details.append({"item": "严格校验总额计算的准确性", "score": 0, "max_score": 30, "passed": False, "reason": "文件格式损坏"})
            details.append({"item": "校验生态指数评分是否存在且合规", "score": 0, "max_score": 20, "passed": False, "reason": "文件格式损坏"})

    output = {
        "total_score": score,
        "details": details
    }
    
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
