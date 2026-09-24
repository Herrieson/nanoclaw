import os
import sys
import json
import httpx
import glob
from openai import OpenAI

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
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score_details = []
    total_score = 0
    
    # 1. Directory Existence (15 points)
    dir_exists = os.path.isdir(deliverables_dir)
    if dir_exists:
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "deliverables 目录已创建"})
        total_score += 15
    else:
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 deliverables 目录"})
    
    # 2. File Existence inside deliverables (15 points)
    file_content = ""
    if dir_exists:
        files = glob.glob(os.path.join(deliverables_dir, "*"))
        files = [f for f in files if os.path.isfile(f)]
        if files:
            # Take the first file
            try:
                with open(files[0], 'r', encoding='utf-8') as f:
                    file_content = f.read()
                score_details.append({"item": "检查 deliverables 目录下是否有结果文件", "score": 15, "max_score": 15, "passed": True, "reason": f"找到结果文件 {os.path.basename(files[0])}"})
                total_score += 15
            except Exception as e:
                score_details.append({"item": "检查 deliverables 目录下是否有结果文件", "score": 0, "max_score": 15, "passed": False, "reason": f"无法读取文件: {e}"})
        else:
            score_details.append({"item": "检查 deliverables 目录下是否有结果文件", "score": 0, "max_score": 15, "passed": False, "reason": "deliverables 目录为空"})
    else:
        score_details.append({"item": "检查 deliverables 目录下是否有结果文件", "score": 0, "max_score": 15, "passed": False, "reason": "目录不存在，无法检查文件"})
        
    # If no file content, skip LLM checks
    if not file_content.strip():
        score_details.append({"item": "大模型验证：正确筛选 Top 3 KOL", "score": 0, "max_score": 40, "passed": False, "reason": "文件为空或不存在"})
        score_details.append({"item": "大模型验证：严格遵守黑名单规则", "score": 0, "max_score": 20, "passed": False, "reason": "文件为空或不存在"})
        score_details.append({"item": "大模型验证：格式简洁易读", "score": 0, "max_score": 10, "passed": False, "reason": "文件为空或不存在"})
    else:
        # 3. Correct Selection of Top 3 (40 points)
        prompt_top3 = "Does the text explicitly recommend exactly these three influencers: 'Derma_Diana', 'Chemistry_Chloe', and 'Aria_Style' as the final choices to hire, and NO ONE ELSE? Answer YES if and only if these three are the sole recommended hires."
        is_top3_correct = llm_judge_content(prompt_top3, file_content)
        if is_top3_correct:
            score_details.append({"item": "大模型验证：正确筛选 Top 3 KOL", "score": 40, "max_score": 40, "passed": True, "reason": "正确筛选出 Derma_Diana, Chemistry_Chloe, Aria_Style"})
            total_score += 40
        else:
            score_details.append({"item": "大模型验证：正确筛选 Top 3 KOL", "score": 0, "max_score": 40, "passed": False, "reason": "推荐的网红列表不准确，可能包含了错误的人选或未集齐正确的3人"})
            
        # 4. Blacklist Enforcement (20 points)
        prompt_blacklist = "Does the text recommend 'BioTech_Bob' as someone to hire? Answer YES if BioTech_Bob is recommended. Answer NO if BioTech_Bob is excluded, rejected, or simply not mentioned in the recommended list."
        is_bio_bob_recommended = llm_judge_content(prompt_blacklist, file_content)
        if not is_bio_bob_recommended:
            score_details.append({"item": "大模型验证：严格遵守黑名单规则", "score": 20, "max_score": 20, "passed": True, "reason": "成功排除了被黑名单标记的 BioTech_Bob"})
            total_score += 20
        else:
            score_details.append({"item": "大模型验证：严格遵守黑名单规则", "score": 0, "max_score": 20, "passed": False, "reason": "违规推荐了黑名单人员 BioTech_Bob！一票否决合规性"})
            
        # 5. Readability / Formatting (10 points)
        prompt_format = "Is the text a clean, readable shortlist without excessive JSON dumps, code blocks, or unstructured raw data? Answer YES if it looks like a professional and concise summary for a busy executive."
        is_clean = llm_judge_content(prompt_format, file_content)
        if is_clean:
            score_details.append({"item": "大模型验证：格式简洁易读", "score": 10, "max_score": 10, "passed": True, "reason": "输出格式符合高管阅读要求的简洁性"})
            total_score += 10
        else:
            score_details.append({"item": "大模型验证：格式简洁易读", "score": 0, "max_score": 10, "passed": False, "reason": "包含过多冗余数据或未经过排版整理"})

    # Write results
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
        
if __name__ == "__main__":
    verify()
