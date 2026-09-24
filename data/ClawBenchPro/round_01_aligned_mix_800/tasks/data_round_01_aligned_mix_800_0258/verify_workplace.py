import os
import sys
import json
import httpx
import pandas as pd
from openai import OpenAI

# 配置环境
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    project_brief_path = os.path.join(workspace, "project_brief")
    results_json = os.path.join(project_brief_path, "usable_equipment.json")
    chart_file = os.path.join(project_brief_path, "bar_chart.txt") # 假设的文件名，提示词要求是文本文件
    
    score = 0
    details = []

    # 1. 目录与文件基础存在性检查 (10分)
    if os.path.exists(project_brief_path):
        score += 5
        details.append({"item": "目录 project_brief 存在", "score": 5, "max_score": 5, "passed": True})
        
        json_exists = any(f.endswith('.json') for f in os.listdir(project_brief_path))
        if json_exists:
            score += 5
            details.append({"item": "JSON 结果文件存在", "score": 5, "max_score": 5, "passed": True})
            # 找到具体的JSON文件路径
            for f in os.listdir(project_brief_path):
                if f.endswith('.json'):
                    results_json = os.path.join(project_brief_path, f)
                    break
        else:
            details.append({"item": "JSON 结果文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "未找到JSON输出"})
    else:
        details.append({"item": "目录与基础文件检查", "score": 0, "max_score": 10, "passed": False, "reason": "目录 project_brief 缺失"})

    # 2. 数据清洗正确性检查 (50分)
    # 标准集推导：
    # A01: Solar, New, 150 (Keep)
    # A02: Wind, Good, 300 (Keep)
    # A03: Fossil (Trash)
    # A04: Hydroponic, Negative Price (Trash)
    # A05: Solar, Refurbished, 400 (Keep)
    # B01: Solar, Damaged (Trash)
    # B02: Hydroponic, New, 50 (Keep)
    # B03: Wind, Missing Price (Trash)
    # B04: Fossil (Trash)
    # B05: Hydroponic, Used, 120 (Keep)
    # 最终应包含: A01, A02, A05, B02, B05
    expected_ids = {"A01", "A02", "A05", "B02", "B05"}
    
    if os.path.exists(results_json):
        try:
            with open(results_json, 'r') as f:
                data = json.load(f)
            
            actual_ids = {str(item['id']).strip().upper() for item in data}
            
            # 检查是否包含多余数据 (尤其是 Fossil 和 Damaged)
            invalid_ids = actual_ids - expected_ids
            missing_ids = expected_ids - actual_ids
            
            if not invalid_ids and not missing_ids:
                score += 30
                details.append({"item": "数据过滤逻辑正确性", "score": 30, "max_score": 30, "passed": True, "reason": "成功提取了所有符合条件的5项数据，并排除了受损、化石能源及价格异常项"})
            elif not invalid_ids and len(actual_ids) > 0:
                current_pts = max(0, 30 - len(missing_ids) * 10)
                score += current_pts
                details.append({"item": "数据过滤逻辑正确性", "score": current_pts, "max_score": 30, "passed": False, "reason": f"未包含多余数据但漏掉了: {missing_ids}"})
            else:
                details.append({"item": "数据过滤逻辑正确性", "score": 0, "max_score": 30, "passed": False, "reason": f"包含了错误数据: {invalid_ids}"})

            # 检查 Category 字段是否是通过 Skill 补全的
            cat_check = all('category' in item and item['category'] in ["Solar", "Wind", "Hydroponic"] for item in data)
            if cat_check:
                score += 20
                details.append({"item": "字段补全准确性", "score": 20, "max_score": 20, "passed": True, "reason": "所有项目均成功补全了正确的 Category"})
            else:
                details.append({"item": "字段补全准确性", "score": 0, "max_score": 20, "passed": False, "reason": "部分项目缺失 Category 字段或分类错误"})

        except Exception as e:
            details.append({"item": "JSON 解析与逻辑校验", "score": 0, "max_score": 50, "passed": False, "reason": f"解析失败: {e}"})

    # 3. 可视化图表检查 (40分)
    chart_files = [f for f in os.listdir(project_brief_path) if f.endswith('.txt')] if os.path.exists(project_brief_path) else []
    if chart_files:
        chart_path = os.path.join(project_brief_path, chart_files[0])
        with open(chart_path, 'r') as f:
            chart_content = f.read()
        
        # 使用 LLM 检查图表是否符合 ASCII 条形图要求且按类别汇总
        prompt = "Check if this file contains an ASCII-style bar chart that visualizes the total cost of equipment grouped by category (Solar, Wind, Hydroponic). Does it look professional for a projector presentation?"
        if llm_judge_content(prompt, chart_content):
            score += 40
            details.append({"item": "ASCII 图表生成", "score": 40, "max_score": 40, "passed": True, "reason": "LLM 判定图表结构清晰，符合演示要求"})
        else:
            score += 15
            details.append({"item": "ASCII 图表生成", "score": 15, "max_score": 40, "passed": False, "reason": "文件存在但 LLM 判定格式不符合 ASCII 条形图标准或缺少类别汇总"})
    else:
        details.append({"item": "ASCII 图表生成", "score": 0, "max_score": 40, "passed": False, "reason": "未找到图表文本文件"})

    # 写入最终得分
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(score), "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
