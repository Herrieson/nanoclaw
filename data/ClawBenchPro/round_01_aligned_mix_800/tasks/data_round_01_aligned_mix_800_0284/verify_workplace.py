import os
import sys
import json
import httpx
import re
from openai import OpenAI

# 强制要求：从环境变量读取配置并关闭 SSL 验证
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
    """统一的非结构化语义验证接口"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        result = response.choices[0].message.content.strip().lower()
        return "yes" in result
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = os.path.join(workspace, "output")
    plan_path = os.path.join(output_dir, "action_plan.json")
    chart_path = os.path.join(output_dir, "hazard_chart.txt")
    
    score_details = []
    
    # 1. 目录与文件存在性 (10分)
    dir_exists = os.path.exists(output_dir)
    plan_exists = os.path.exists(plan_path)
    chart_exists = os.path.exists(chart_path)
    score_details.append({
        "item": "基础文件结构检查",
        "score": 10 if dir_exists and plan_exists and chart_exists else 0,
        "max_score": 10,
        "passed": dir_exists and plan_exists and chart_exists,
        "reason": "output目录及必要文件齐全" if dir_exists and plan_exists and chart_exists else "缺失必要输出文件"
    })

    # 2. action_plan.json 结构与志愿者筛选 (30分)
    # 标准：Samuel (clearing), Marie (clearing) 应在名单中。David, Chloe, Jerome 不在。
    vol_score = 0
    vol_reason = ""
    if plan_exists:
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                vols = data.get("capable_volunteers", [])
                vols_set = set([v.lower() for v in vols])
                expected_vols = {"samuel", "marie"}
                forbidden_vols = {"david", "chloe", "jerome"}
                
                if expected_vols.issubset(vols_set) and not (vols_set & forbidden_vols):
                    vol_score = 30
                    vol_reason = "志愿者筛选完全正确（Samuel, Marie）"
                elif expected_vols.issubset(vols_set):
                    vol_score = 15
                    vol_reason = "包含了正确志愿者但混入了无关人员"
                else:
                    vol_reason = f"志愿者筛选错误，识别到: {list(vols_set)}"
        except Exception as e:
            vol_reason = f"JSON解析失败: {str(e)}"
    
    score_details.append({"item": "志愿者能力筛选验证", "score": vol_score, "max_score": 30, "passed": vol_score == 30, "reason": vol_reason})

    # 3. 危险路径识别与工具提取 (40分)
    # 标准：Hazard > 3 的路径：Bear Creek(5), Summit Path(4), Canyon Descent(6)
    # 对应工具：Chainsaw, Gravel Truck, Heavy Excavator
    trail_score = 0
    trail_reason = ""
    if plan_exists:
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                trails = data.get("dangerous_trails", [])
                # 建立标准答案
                truth = {
                    "bear creek": "chainsaw",
                    "summit path": "gravel truck",
                    "canyon descent": "heavy excavator"
                }
                found_count = 0
                for t in trails:
                    name = t.get("trail_name", "").lower()
                    tool = t.get("recommended_tool", "").lower()
                    if name in truth and truth[name] in tool:
                        found_count += 1
                
                if found_count == 3 and len(trails) == 3:
                    trail_score = 40
                    trail_reason = "所有危险路径(>3)及配套工具识别准确"
                else:
                    trail_score = (found_count * 10)
                    trail_reason = f"路径识别不完整或工具错误，正确匹配数: {found_count}"
        except:
            trail_reason = "无法读取路径数据"

    score_details.append({"item": "危险路径与工具推荐验证", "score": trail_score, "max_score": 40, "passed": trail_score == 40, "reason": trail_reason})

    # 4. ASCII 图表可视化 (20分)
    # 标准：检查文件中是否包含 ASCII 柱状特征，以及数值是否正确。
    chart_score = 0
    chart_reason = ""
    if chart_exists:
        with open(chart_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 使用 LLM 检查图表逻辑：是否为 Bear Creek(5), Summit Path(4), Canyon Descent(6) 绘制了柱状图
            prompt = "Check if this file contains a simple ASCII bar chart showing hazard levels for Bear Creek (level 5), Summit Path (level 4), and Canyon Descent (level 6). It should use characters like # or * to represent the values."
            if llm_judge_content(prompt, content):
                chart_score = 20
                chart_reason = "ASCII 图表语义与数值逻辑符合要求"
            else:
                chart_reason = "图表内容不匹配或未按要求绘制危险路径"
    
    score_details.append({"item": "ASCII 图表语义验证", "score": chart_score, "max_score": 20, "passed": chart_score == 20, "reason": chart_reason})

    # 汇总
    total_score = sum(d["score"] for d in score_details)
    output_result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output_result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
