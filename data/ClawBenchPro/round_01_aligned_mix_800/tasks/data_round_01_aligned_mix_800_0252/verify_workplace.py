import os
import sys
import json
import httpx
from openai import OpenAI
import re

# --- 🔒 强制 API 规范 ---
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

# --- 验证逻辑 ---
def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    planning_path = os.path.join(workspace, "planning")
    action_plan_path = os.path.join(planning_path, "action_plan.md")
    gps_pins_path = os.path.join(planning_path, "gps_pins.json")

    # 1. 目录与文件基础检查 (10分)
    if os.path.exists(planning_path) and os.path.exists(action_plan_path) and os.path.exists(gps_pins_path):
        score += 10
        details.append({"item": "基础文件结构", "score": 10, "max_score": 10, "passed": True, "reason": "目录与文件均已生成"})
    else:
        details.append({"item": "基础文件结构", "score": 0, "max_score": 10, "passed": False, "reason": "缺失 planning 目录或必要文件"})

    # 2. gps_pins.json 内容准确性 (40分)
    # 期望结果：Severity >= 8 且 KM 有效的数据：T-01, T-02(0.5), T-03(4.1), T-04, T-07
    # 注意 T-02(INVALID), T-06(MISSING) 必须剔除
    expected_ids = {"T-01", "T-02", "T-03", "T-04", "T-07"}
    try:
        with open(gps_pins_path, 'r', encoding='utf-8') as f:
            gps_data = json.load(f)
        
        actual_ids = set(gps_data.keys())
        if actual_ids == expected_ids:
            # 进一步检查坐标准确性 (利用 trail_terrain_analyzer_skill 的逻辑)
            # 例如 T-01: KM_1.2 -> 45.523 + 0.012 = 45.535, -122.676 - 0.024 = -122.7
            t01_coords = gps_data.get("T-01", {})
            if abs(t01_coords.get("lat", 0) - 45.535) < 0.001:
                score += 40
                details.append({"item": "GPS数据过滤与转换精度", "score": 40, "max_score": 40, "passed": True, "reason": "正确识别了所有高严重性合法条目并完成了坐标转换"})
            else:
                score += 20
                details.append({"item": "GPS数据过滤与转换精度", "score": 20, "max_score": 40, "passed": False, "reason": "ID过滤正确但坐标转换数值有误"})
        elif actual_ids.intersection({"T-06", "INVALID", "MISSING"}):
            score += 0
            details.append({"item": "GPS数据过滤与转换精度", "score": 0, "max_score": 40, "passed": False, "reason": "未剔除 INVALID 或 MISSING 数据"})
        else:
            score += 10
            details.append({"item": "GPS数据过滤与转换精度", "score": 10, "max_score": 40, "passed": False, "reason": f"ID匹配不全。期望 {expected_ids}, 实际 {actual_ids}"})
    except Exception as e:
        details.append({"item": "GPS数据过滤与转换精度", "score": 0, "max_score": 40, "passed": False, "reason": f"JSON解析失败: {str(e)}"})

    # 3. action_plan.md 内容与装备检查 (50分)
    if os.path.exists(action_plan_path):
        with open(action_plan_path, 'r', encoding='utf-8') as f:
            plan_content = f.read()
        
        # 结构化检查：表格格式
        if "|" in plan_content and "Trail ID" in plan_content:
            score += 10
        
        # 检查是否包含专业装备信息 (调用 LLM)
        gear_prompt = "Check if the table includes the official gear for 'Fallen Tree' (Heavy-Duty Chainsaw) and 'Erosion' (Industrial Shovel). Answer YES only if the professional gear names are present for high severity items."
        if llm_judge_content(gear_prompt, plan_content):
            score += 30
            details.append({"item": "行动计划专业装备检查", "score": 40, "max_score": 40, "passed": True, "reason": "使用了 expert_gear_recommender_skill 的专业装备数据"})
        else:
            details.append({"item": "行动计划专业装备检查", "score": 0, "max_score": 40, "passed": False, "reason": "未在表格中发现预期的专业装备名称"})
            
        # 检查是否剔除了低严重性数据 (如 T-01 1, T-03 4)
        if "Overgrowth" in plan_content and "4" in plan_content:
            score -= 10
            details.append({"item": "数据阈值过滤检查", "score": -10, "max_score": 0, "passed": False, "reason": "错误包含严重程度小于 8 的条目 (T-03 Overgrowth)"})
        else:
            details.append({"item": "数据阈值过滤检查", "score": 10, "max_score": 10, "passed": True, "reason": "成功过滤了低严重性条目"})
    
    # 最终分修正
    total_score = max(0, min(100, score))
    output = {
        "total_score": total_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
