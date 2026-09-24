import os
import sys
import json
import httpx
import re
from openai import OpenAI

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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    reports_dir = os.path.join(workspace, "reports")
    
    score_details = []
    total_score = 0
    
    # 1. 检查目录及文件存在性 (10分)
    report_content = ""
    report_file_found = False
    if os.path.isdir(reports_dir):
        files = [f for f in os.listdir(reports_dir) if os.path.isfile(os.path.join(reports_dir, f))]
        if files:
            report_file_found = True
            with open(os.path.join(reports_dir, files[0]), 'r', encoding='utf-8') as f:
                report_content = f.read()
            score_details.append({"item": "检查报告目录及文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": f"找到报告文件: {files[0]}"})
            total_score += 10
        else:
            score_details.append({"item": "检查报告目录及文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "reports 目录存在但无文件"})
    else:
        score_details.append({"item": "检查报告目录及文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 reports 目录"})

    # 如果没有找到报告，直接输出零分项
    if not report_file_found:
        score_details.extend([
            {"item": "精确提取V2-Neon受影响的仓库及防止幻觉", "score": 0, "max_score": 40, "passed": False, "reason": "无文件可验证"},
            {"item": "计算准确的平均舒适度", "score": 0, "max_score": 30, "passed": False, "reason": "无文件可验证"},
            {"item": "大模型语义检查: 汇报语气与业务紧迫性", "score": 0, "max_score": 20, "passed": False, "reason": "无文件可验证"}
        ])
    else:
        # 2. 精确提取V2-Neon受影响的仓库及防止幻觉 (40分)
        # 正确的仓库应该是 Chicago-Midwest 和 Atlanta-East
        correct_hubs = ["Chicago-Midwest", "Atlanta-East"]
        incorrect_hubs = ["Seattle-NW", "Dallas-South", "Miami-SE", "Denver-Mountain"]
        
        has_chicago = "Chicago-Midwest".lower() in report_content.lower()
        has_atlanta = "Atlanta-East".lower() in report_content.lower()
        has_hallucination = any(hub.lower() in report_content.lower() for hub in incorrect_hubs)
        
        hub_score = 0
        if has_chicago and has_atlanta:
            hub_score = 40
            reason = "准确找出了所有受影响的仓库且无幻觉。"
            if has_hallucination:
                hub_score = 10  # 严重扣分
                reason = "找出了受影响的仓库，但捏造了未受影响的仓库，导致召回范围错误！严重扣分。"
        elif has_chicago or has_atlanta:
            hub_score = 20
            reason = "只找出部分受影响的仓库。"
        else:
            hub_score = 0
            reason = "未找出正确的受影响仓库。"
            
        score_details.append({"item": "精确提取V2-Neon受影响的仓库及防止幻觉", "score": hub_score, "max_score": 40, "passed": hub_score == 40, "reason": reason})
        total_score += hub_score

        # 3. 计算准确的平均舒适度 (30分)
        # 评分：4, 3, 5, 2 => 平均 14/4 = 3.5
        if "3.5" in report_content:
            score_details.append({"item": "计算准确的平均舒适度", "score": 30, "max_score": 30, "passed": True, "reason": "准确计算并输出了平均舒适度 3.5。"})
            total_score += 30
        else:
            score_details.append({"item": "计算准确的平均舒适度", "score": 0, "max_score": 30, "passed": False, "reason": "报告中未找到正确的平均舒适度数值(3.5)。"})

        # 4. 大模型语义检查: 汇报语气与业务紧迫性 (20分)
        prompt = "Does this report sound like a formal business brief addressing the 'V2-Neon' battery defect recall and overall comfort ratings? It must have a formal and urgent tone suitable for a steering committee."
        is_formal = llm_judge_content(prompt, report_content)
        if is_formal:
            score_details.append({"item": "大模型语义检查: 汇报语气与业务紧迫性", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定报告具备高管汇报所需的正式与紧迫语气。"})
            total_score += 20
        else:
            score_details.append({"item": "大模型语义检查: 汇报语气与业务紧迫性", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定报告缺乏正式商业简报的结构或语气。"})

    # 输出结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
