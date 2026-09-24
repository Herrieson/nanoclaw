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

def verify_workplace(workspace):
    score_details = []
    total_score = 0
    
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    # 1. 检查 deliverables 目录是否存在
    if os.path.isdir(deliverables_dir):
        score_details.append({"item": "Check if 'deliverables' directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "'deliverables' directory found."})
        total_score += 10
    else:
        score_details.append({"item": "Check if 'deliverables' directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "'deliverables' directory is missing."})
        
    # 2. 检查输出文件
    file_content = ""
    if os.path.isdir(deliverables_dir):
        files = [f for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]
        if files:
            score_details.append({"item": "Check if there are files in 'deliverables' directory", "score": 10, "max_score": 10, "passed": True, "reason": "Output file(s) found."})
            total_score += 10
            
            # 读取所有文件内容合并
            for fname in files:
                try:
                    with open(os.path.join(deliverables_dir, fname), "r", encoding="utf-8") as f:
                        file_content += f.read() + "\n"
                except Exception:
                    pass
        else:
            score_details.append({"item": "Check if there are files in 'deliverables' directory", "score": 0, "max_score": 10, "passed": False, "reason": "No files found in 'deliverables' directory."})
    else:
        score_details.append({"item": "Check if there are files in 'deliverables' directory", "score": 0, "max_score": 10, "passed": False, "reason": "Directory does not exist."})
        
    # 3. LLM 检查：安全违规项提取是否准确且无幻觉
    if file_content.strip():
        prompt_violations = (
            "Does the document accurately list EXACTLY these three safety hazards/violations: "
            "1) crew missing hardhats, 2) scaffolding unstable, 3) extension cord in a puddle? "
            "It must NOT include any false/hallucinated violations, and must mention these three specifically."
        )
        passed_violations = llm_judge_content(prompt_violations, file_content)
        if passed_violations:
            score_details.append({"item": "LLM check: Accurate safety violations extracted", "score": 30, "max_score": 30, "passed": True, "reason": "Document correctly lists the specific safety violations."})
            total_score += 30
        else:
            score_details.append({"item": "LLM check: Accurate safety violations extracted", "score": 0, "max_score": 30, "passed": False, "reason": "Document failed to list the correct safety violations or included hallucinated ones."})
            
        # 4. LLM 检查：安全费用计算是否准确 (150 + 120 + 15.50 + 25 = 310.50)
        prompt_cost = (
            "Does the document explicitly state the total safety expenses are exactly 310.50 (or 310.5) "
            "and clearly indicate this is the total for safety gear/expenses?"
        )
        passed_cost = llm_judge_content(prompt_cost, file_content)
        if passed_cost:
            score_details.append({"item": "LLM check: Exact safety expense total calculation", "score": 30, "max_score": 30, "passed": True, "reason": "Document correctly reports the total safety expense as 310.50."})
            total_score += 30
        else:
            score_details.append({"item": "LLM check: Exact safety expense total calculation", "score": 0, "max_score": 30, "passed": False, "reason": "Document does not report the exact total of 310.50 or misrepresents it."})
            
        # 5. LLM 检查：是否排除了个人艺术用品的信息
        prompt_personal = (
            "Does the document completely exclude ANY mention of personal items, art supplies, paints, "
            "canvas, clay, or the personal expense total? Answer 'YES' if they are completely excluded, 'NO' if any are mentioned."
        )
        passed_personal = llm_judge_content(prompt_personal, file_content)
        if passed_personal:
            score_details.append({"item": "LLM check: Exclusion of personal/art expenses", "score": 20, "max_score": 20, "passed": True, "reason": "Document properly excludes all personal and art-related items."})
            total_score += 20
        else:
            score_details.append({"item": "LLM check: Exclusion of personal/art expenses", "score": 0, "max_score": 20, "passed": False, "reason": "Document incorrectly includes personal or art-related items."})
    else:
        score_details.append({"item": "LLM check: Accurate safety violations extracted", "score": 0, "max_score": 30, "passed": False, "reason": "Empty or unreadable output."})
        score_details.append({"item": "LLM check: Exact safety expense total calculation", "score": 0, "max_score": 30, "passed": False, "reason": "Empty or unreadable output."})
        score_details.append({"item": "LLM check: Exclusion of personal/art expenses", "score": 0, "max_score": 20, "passed": False, "reason": "Empty or unreadable output."})

    # 写入结果
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace_path)
