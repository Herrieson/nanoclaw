import os
import sys
import json
import httpx
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
    # 此函数为检测非结构化文本的统一接口
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
    audit_dir = os.path.join(workspace, "audit_results")
    
    score_details = []
    total_score = 0
    
    # 1. Check Directory (10 points)
    dir_exists = os.path.isdir(audit_dir)
    if dir_exists:
        score_details.append({"item": "检查结果目录 audit_results 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 audit_results 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录 audit_results 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 audit_results 目录"})
        
    # 2. Check File & Read Content (10 points)
    report_content = ""
    file_found = False
    if dir_exists:
        files = os.listdir(audit_dir)
        if files:
            file_found = True
            score_details.append({"item": "检查目录内是否存在总结文件", "score": 10, "max_score": 10, "passed": True, "reason": f"找到文件: {', '.join(files)}"})
            total_score += 10
            for f in files:
                file_path = os.path.join(audit_dir, f)
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                        report_content += file.read() + "\n"
        else:
            score_details.append({"item": "检查目录内是否存在总结文件", "score": 0, "max_score": 10, "passed": False, "reason": "audit_results 目录为空"})
    else:
        score_details.append({"item": "检查目录内是否存在总结文件", "score": 0, "max_score": 10, "passed": False, "reason": "前置目录缺失，无法验证文件"})

    # Semantic Validations using LLM (80 points total)
    if report_content.strip():
        # 3. Ghosts Identification (25 points)
        prompt_ghosts = "Does the text explicitly identify BOTH 'Marcus Vane' and 'Sheila Reed' as 'ghosts', 'unauthorized', or 'not on the master roster'? Both names must be clearly flagged as unauthorized."
        if llm_judge_content(prompt_ghosts, report_content):
            score_details.append({"item": "识别 'Ghosts' 幽灵护士", "score": 25, "max_score": 25, "passed": True, "reason": "成功识别出 Marcus Vane 和 Sheila Reed 为非名单内员工"})
            total_score += 25
        else:
            score_details.append({"item": "识别 'Ghosts' 幽灵护士", "score": 0, "max_score": 25, "passed": False, "reason": "未能准确或完整识别出两名幽灵护士"})

        # 4. Overtime Calculation (35 points)
        # Bernice: 15.5 * 85 = 1317.5
        # Althea: 8 * 85 = 680
        # Cedric: 5.25 * 85 = 446.25
        prompt_calcs = "Does the text state the EXACT overtime pay calculations for the following legitimate staff: Bernice Thompson = $1317.50 (or 1317.5), Althea Richards = $680.00 (or 680), Cedric Miller = $446.25? All three correct numeric values must be present and associated with the correct names."
        if llm_judge_content(prompt_calcs, report_content):
            score_details.append({"item": "精确计算加班费", "score": 35, "max_score": 35, "passed": True, "reason": "所有合法员工的加班费计算完全准确"})
            total_score += 35
        else:
            score_details.append({"item": "精确计算加班费", "score": 0, "max_score": 35, "passed": False, "reason": "加班费计算有误或未给出具体数值"})

        # 5. High Fatigue Warning (10 points)
        prompt_fatigue = "Does the text assign a 'High Fatigue Warning' flag to 'Bernice Thompson', and ONLY to her (she has >12 hours)?"
        if llm_judge_content(prompt_fatigue, report_content):
            score_details.append({"item": "高疲劳警告标识", "score": 10, "max_score": 10, "passed": True, "reason": "正确为超负荷工作的员工打上 High Fatigue Warning 标签"})
            total_score += 10
        else:
            score_details.append({"item": "高疲劳警告标识", "score": 0, "max_score": 10, "passed": False, "reason": "未能正确标识高疲劳警告，或将其错误赋予其他员工"})

        # 6. Professional Tone (10 points)
        prompt_tone = "Is the text formatted as a clean, professional summary report appropriate for a medical clinical setting? It should not just be a raw JSON or raw script dump."
        if llm_judge_content(prompt_tone, report_content):
            score_details.append({"item": "文本专业度评估", "score": 10, "max_score": 10, "passed": True, "reason": "报告结构清晰，符合护士长的专业要求"})
            total_score += 10
        else:
            score_details.append({"item": "文本专业度评估", "score": 0, "max_score": 10, "passed": False, "reason": "文本格式杂乱或缺乏专业排版"})
    else:
        # If no content, fail all semantic checks
        for item, score in [("识别 'Ghosts' 幽灵护士", 25), ("精确计算加班费", 35), ("高疲劳警告标识", 10), ("文本专业度评估", 10)]:
            score_details.append({"item": item, "score": 0, "max_score": score, "passed": False, "reason": "文件为空或不存在，无法评估"})

    # Output results
    result_data = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
