import os
import sys
import json
import glob
import httpx
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    finance_summary_dir = os.path.join(workspace, "finance_summary")
    
    score_details = []
    total_score = 0
    
    # Check 1: Directory and File existence
    files_found = []
    if os.path.isdir(finance_summary_dir):
        files_found = [f for f in os.listdir(finance_summary_dir) if os.path.isfile(os.path.join(finance_summary_dir, f))]
        
    if files_found:
        score_details.append({"item": "检查 finance_summary 目录及文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": f"找到文件: {files_found[0]}"})
        total_score += 20
    else:
        score_details.append({"item": "检查 finance_summary 目录及文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 finance_summary 目录或目录为空"})
    
    # If file exists, proceed with content checks
    if files_found:
        file_path = os.path.join(finance_summary_dir, files_found[0])
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Check 2: Net Cash Calculation (LLM Check)
            prompt_net_cash = "Check if the document explicitly states that the final net cash (or actual cash in pocket) is exactly 75.50. The value must be 75.50 (or 75.5) and it must be clearly identified as the final net income after subtracting all expenses from the paid amount. Does it correctly state 75.50?"
            if llm_judge_content(prompt_net_cash, content):
                score_details.append({"item": "大模型检查净收入计算正确性 (75.50)", "score": 40, "max_score": 40, "passed": True, "reason": "成功提取并验证净收入为 75.50"})
                total_score += 40
            else:
                score_details.append({"item": "大模型检查净收入计算正确性 (75.50)", "score": 0, "max_score": 40, "passed": False, "reason": "文档中未包含正确的净收入 (75.50) 或计算错误"})
                
            # Check 3: Debtors List (LLM Check)
            prompt_debtors = "Check if the document clearly lists the following specific individuals as people who owe money (debtors): Elena, Mrs. Smith, and Sofia. It MUST include all three of them, and NO ONE ELSE should be listed as a debtor. Does it correctly list exactly these three?"
            if llm_judge_content(prompt_debtors, content):
                score_details.append({"item": "大模型检查欠款人名单准确性", "score": 40, "max_score": 40, "passed": True, "reason": "准确列出了所有三个欠款人，且无多余人员"})
                total_score += 40
            else:
                score_details.append({"item": "大模型检查欠款人名单准确性", "score": 0, "max_score": 40, "passed": False, "reason": "欠款人名单不完整、包含多余人员或未提及"})
                
        except Exception as e:
            score_details.append({"item": "读取总结文件", "score": 0, "max_score": 80, "passed": False, "reason": f"文件读取失败: {str(e)}"})
    else:
        score_details.append({"item": "大模型检查净收入计算正确性 (75.50)", "score": 0, "max_score": 40, "passed": False, "reason": "缺少目标文件，无法检查"})
        score_details.append({"item": "大模型检查欠款人名单准确性", "score": 0, "max_score": 40, "passed": False, "reason": "缺少目标文件，无法检查"})

    # Write output score
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
