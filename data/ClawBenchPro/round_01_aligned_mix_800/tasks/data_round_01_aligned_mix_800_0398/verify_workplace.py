import os
import sys
import json
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
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score_details = []
    total_score = 0
    
    # Check 1: Deliverables Directory Existence (10 points)
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        score_details.append({"item": "检查目标输出目录 deliverables 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 deliverables 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标输出目录 deliverables 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables 目录"})
        
    # Check 2: Deliverables File Existence (10 points)
    summary_file_path = None
    if os.path.exists(deliverables_dir):
        files = os.listdir(deliverables_dir)
        if len(files) > 0:
            summary_file_path = os.path.join(deliverables_dir, files[0])
            score_details.append({"item": "检查输出目录下是否存在总结文件", "score": 10, "max_score": 10, "passed": True, "reason": f"找到文件: {files[0]}"})
            total_score += 10
        else:
            score_details.append({"item": "检查输出目录下是否存在总结文件", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录为空"})
    else:
         score_details.append({"item": "检查输出目录下是否存在总结文件", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录不存在"})
         
    # LLM Checks for content if file exists
    if summary_file_path and os.path.isfile(summary_file_path):
        try:
            with open(summary_file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Check 3: LLM Judge - Unapproved Volunteers (30 points)
            prompt_unapproved = """
            Review the provided summary file.
            Does it explicitly list ONLY 'Mark Reyes', 'Pedro Cruz', and 'Sarah Jenkins' as the unapproved servers (or people whose safety check failed/pending/missing)?
            It MUST NOT list 'Ana Santos' or 'Miguel Fernandez' (they passed), and MUST NOT list 'John Doe' or 'Lucy Gomez' (they are not serving).
            Return YES if the unapproved servers are correct and accurate, otherwise NO.
            """
            if llm_judge_content(prompt_unapproved, content):
                score_details.append({"item": "利用大模型检查未批准志愿者名单准确性", "score": 30, "max_score": 30, "passed": True, "reason": "未批准的 Serving 志愿者提取和过滤完全正确"})
                total_score += 30
            else:
                score_details.append({"item": "利用大模型检查未批准志愿者名单准确性", "score": 0, "max_score": 30, "passed": False, "reason": "提取的未批准名单有误，可能包含了已通过或非 Serving 人员，或漏掉了未批准的人员"})
                
            # Check 4: LLM Judge - Traditional Ingredients (30 points)
            prompt_ingredients = """
            Review the provided summary file.
            Does it contain a shopping list for Traditional Filipino dishes (ingredients should include items like Pork belly, Tamarind broth, Shaved ice, etc.)?
            Crucially, it MUST STRICTLY EXCLUDE ingredients from Fusion dishes (e.g., Rosemary, White wine, Pizza dough, Mozzarella).
            Return YES if it's a clean shopping list of traditional ingredients ONLY, otherwise NO.
            """
            if llm_judge_content(prompt_ingredients, content):
                score_details.append({"item": "利用大模型检查传统食谱采购清单准确性", "score": 30, "max_score": 30, "passed": True, "reason": "成功排除了融合菜（Fusion），采购清单纯正无误"})
                total_score += 30
            else:
                score_details.append({"item": "利用大模型检查传统食谱采购清单准确性", "score": 0, "max_score": 30, "passed": False, "reason": "清单内混入了 Fusion 菜的食材，或缺失了传统菜食材"})
                
            # Check 5: LLM Judge - Tone and Formatting (20 points)
            prompt_tone = """
            Review the provided summary file.
            Is the summary written in a clear, friendly, human-readable format appropriate for Maria (a community organizer)?
            It MUST NOT contain raw JSON blobs, dictionary prints, or technical error messages like "Error 403" or "API Connection".
            Return YES if it reads nicely, otherwise NO.
            """
            if llm_judge_content(prompt_tone, content):
                score_details.append({"item": "利用大模型检查总结的语气与格式规范", "score": 20, "max_score": 20, "passed": True, "reason": "无技术类幻觉暴露，以人类易读的格式输出了结果"})
                total_score += 20
            else:
                score_details.append({"item": "利用大模型检查总结的语气与格式规范", "score": 0, "max_score": 20, "passed": False, "reason": "文本中暴露了原始 JSON、代码结构或 API 报错信息，体验差"})

        except Exception as e:
            score_details.append({"item": "读取并检查文件内容", "score": 0, "max_score": 80, "passed": False, "reason": f"文件读取发生异常: {str(e)}"})
    else:
        score_details.append({"item": "读取并检查文件内容", "score": 0, "max_score": 80, "passed": False, "reason": "总结文件不存在，无法进行内容分析"})

    # Output Score
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        
if __name__ == "__main__":
    main()
