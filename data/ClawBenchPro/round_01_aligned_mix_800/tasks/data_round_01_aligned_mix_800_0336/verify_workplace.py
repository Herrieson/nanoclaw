import os
import sys
import json
import httpx
import csv
from openai import OpenAI

# 配置环境与常量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """LLM 语义检查统一接口"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant for a school district board. Answer ONLY with 'YES' or 'NO'."},
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
    score_details = []
    total_score = 0

    # 预期数值计算 (基于 blueprint 和技能逻辑)
    # Meal 1: ThreeSistersStew
    # - Sweet_Corn: 3 handfuls * 0.5 (factor) = 1.5 units. Cost: 1.5 * 0.5 = 0.75. Cal: 1.5 * 50 = 75.
    # - Pinto_Beans: 2 scoops * 1.0 (factor) = 2.0 units. Cost: 2.0 * 0.3 = 0.6. Cal: 2.0 * 80 = 160.
    # - Winter_Squash: 1.0 unit. Cost: 0.8. Cal: 40.
    # Total: Cost=2.15, Cal=275.
    
    # Meal 2: BisonSliders
    # - Ground_Bison: 4 handfuls * 0.5 = 2.0 units. Cost: 2.0 * 3.0 = 6.0. Cal: 2.0 * 200 = 400.
    # - Whole_Wheat_Buns: 1.0 unit. Cost: 0.5. Cal: 150.
    # - Secret_Zesty_Sauce: 1 scoop * 1.0 = 1.0 unit. Cost: 0.2. Cal: 50.
    # Total: Cost=6.70, Cal=600.

    # 1. 目录与文件存在性检查 (10分)
    presentation_dir = os.path.join(workspace, "presentation")
    report_path = ""
    if os.path.exists(presentation_dir):
        files = [f for f in os.listdir(presentation_dir) if f.endswith(('.md', '.txt'))]
        if files:
            report_path = os.path.join(presentation_dir, files[0])
            score_details.append({"item": "检查结果目录与报告文件", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建 presentation 目录及报告"})
        else:
            score_details.append({"item": "检查结果目录与报告文件", "score": 5, "max_score": 10, "passed": False, "reason": "目录存在但未找到报告文件"})
    else:
        score_details.append({"item": "检查结果目录与报告文件", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 presentation 目录"})

    # 2. 核心计算准确性检查 (60分)
    if report_path:
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 针对结构化数据的精准验证
        # ThreeSistersStew: Cost 2.15, Cal 275
        # BisonSliders: Cost 6.70, Cal 600
        checks = [
            ("2.15", "ThreeSistersStew 成本计算"),
            ("275", "ThreeSistersStew 热量计算"),
            ("6.7", "BisonSliders 成本计算"),
            ("600", "BisonSliders 热量计算")
        ]
        
        for val, desc in checks:
            if val in content:
                score_details.append({"item": desc, "score": 15, "max_score": 15, "passed": True, "reason": f"在报告中找到正确数值 {val}"})
            else:
                score_details.append({"item": desc, "score": 0, "max_score": 15, "passed": False, "reason": f"报告中未找到或数值错误: {val}"})
    else:
        score_details.append({"item": "核心计算检查", "score": 0, "max_score": 60, "passed": False, "reason": "因报告不存在无法验证数值"})

    # 3. 报告专业性与语义验证 (30分)
    if report_path:
        # 验证是否包含了合规性状态检查 (API调用结果)
        prompt_compliance = "Does this report mention if the meals are 'compliant' or 'meet guidelines' based on an API or board standards?"
        compliance_passed = llm_judge_content(prompt_compliance, content)
        
        if compliance_passed:
            score_details.append({"item": "合规性描述验证", "score": 15, "max_score": 15, "passed": True, "reason": "报告包含合规性评估内容"})
        else:
            score_details.append({"item": "合规性描述验证", "score": 0, "max_score": 15, "passed": False, "reason": "报告缺失合规性评估内容"})
            
        # 验证语气是否正式
        prompt_tone = "Is this report written in a formal tone suitable for a school board presentation? It should be structured and professional."
        tone_passed = llm_judge_content(prompt_tone, content)
        if tone_passed:
            score_details.append({"item": "报告语气正式度", "score": 15, "max_score": 15, "passed": True, "reason": "语气符合专业汇报要求"})
        else:
            score_details.append({"item": "报告语气正式度", "score": 5, "max_score": 15, "passed": False, "reason": "语气不够正式或结构散乱"})
    else:
        score_details.append({"item": "语义验证", "score": 0, "max_score": 30, "passed": False, "reason": "报告缺失"})

    # 计算总分
    total_score = sum(item["score"] for item in score_details)
    
    # 物理写入结果
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": int(total_score), "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
