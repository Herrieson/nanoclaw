import os
import sys
import json
import httpx
import glob
import re
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

def verify_workplace(workspace_dir):
    details = []
    total_score = 0
    
    # 1. Check directory and file creation (10 pts)
    briefing_dir = os.path.join(workspace_dir, "briefing")
    report_files = []
    if os.path.exists(briefing_dir) and os.path.isdir(briefing_dir):
        report_files = [os.path.join(briefing_dir, f) for f in os.listdir(briefing_dir) if os.path.isfile(os.path.join(briefing_dir, f))]
        
    if report_files:
        details.append({"item": "检查汇报目录与文件", "score": 10, "max_score": 10, "passed": True, "reason": f"成功在 briefing 目录下生成了汇报文件: {report_files[0]}"})
        total_score += 10
    else:
        details.append({"item": "检查汇报目录与文件", "score": 0, "max_score": 10, "passed": False, "reason": "未能在 briefing 目录下找到任何汇报文件"})
        # 提前终止，后续无法测试
        with open(os.path.join(workspace_dir, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 2. Check content precision using code-based exact matching (40 pts)
    with open(report_files[0], "r", encoding="utf-8") as f:
        report_content = f.read()

    poachers = ["CA-9FAKE00", "CA-BAD888"]
    registered = ["CA-5GTR222", "CA-1ABC123", "CA-8HJK999"]
    
    poachers_found = [p for p in poachers if p in report_content]
    registered_found = [r for r in registered if r in report_content]
    
    content_score = 0
    content_reasons = []
    
    if len(poachers_found) == 2:
        content_score += 20
        content_reasons.append("成功提取并汇报了所有未注册的违规车牌")
    elif len(poachers_found) == 1:
        content_score += 10
        content_reasons.append(f"仅汇报了部分未注册车牌: {poachers_found}")
    else:
        content_reasons.append("未能找到任何未注册车牌")

    if len(registered_found) == 0:
        content_score += 20
        content_reasons.append("正确过滤了已注册的合法车牌，无多余干扰数据")
    else:
        content_reasons.append(f"错误地将已注册的合法车牌包含在报告中: {registered_found}")
        
    details.append({
        "item": "核心车牌数据精准度核验",
        "score": content_score,
        "max_score": 40,
        "passed": content_score == 40,
        "reason": "; ".join(content_reasons)
    })
    total_score += content_score

    # 3. Check Skill Usage Logs for physical side effects (30 pts)
    logs_file = os.path.join(workspace_dir, "logs", "skill_usage.jsonl")
    log_score = 0
    log_reasons = []
    
    if os.path.exists(logs_file):
        used_ocr_visual = False
        used_ocr_audio = False
        api_queries = set()
        
        with open(logs_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    if record.get("skill") == "ocr_license_extractor":
                        inp = record.get("input", "")
                        if "visual_scans" in inp: used_ocr_visual = True
                        if "voice_memo" in inp or "memo" in inp: used_ocr_audio = True
                    elif record.get("skill") == "state_dmv_query_api":
                        api_queries.add(record.get("plate", ""))
                except:
                    continue
                    
        if used_ocr_visual and used_ocr_audio:
            log_score += 15
            log_reasons.append("正确调用 OCR 工具处理了 PDF 图像和音频备忘录")
        elif used_ocr_visual or used_ocr_audio:
            log_score += 5
            log_reasons.append("仅部分处理了源文件（漏掉了 PDF 或音频）")
        else:
            log_reasons.append("未能成功调用 OCR 工具处理指定文件")
            
        if len(api_queries) >= 5 and "CA-9FAKE00" in api_queries and "CA-BAD888" in api_queries:
            log_score += 15
            log_reasons.append("充分调用 DMV 查询 API 验证了提取出的所有车牌")
        elif len(api_queries) > 0:
            log_score += 10
            log_reasons.append("部分调用了 DMV 查询 API")
        else:
            log_reasons.append("未能调用 DMV 查询 API 进行验证")
    else:
        log_reasons.append("未找到工具调用日志，Agent涉嫌纯粹凭空捏造数据")
        
    details.append({
        "item": "验证工具副作用与调用逻辑",
        "score": log_score,
        "max_score": 30,
        "passed": log_score == 30,
        "reason": "; ".join(log_reasons)
    })
    total_score += log_score

    # 4. LLM Semantic Evaluation (20 pts)
    # 警官 Mateo 要求一份给长官的“clean, professional summary”
    prompt_text = (
        "Check if the following report meets these criteria:\n"
        "1. It is formatted as a professional briefing summary intended for a Police Captain.\n"
        "2. The tone is clean, formal, and direct without any conversational fluff.\n"
        "3. It explicitly states that the mentioned plates belong to unregistered vehicles or poachers.\n"
        "Does the text meet ALL these criteria?"
    )
    is_professional = llm_judge_content(prompt_text, report_content)
    if is_professional:
        details.append({
            "item": "利用大模型检查汇报语气与专业度",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "大模型判定报告内容干净、专业、符合给长官汇报的要求"
        })
        total_score += 20
    else:
        details.append({
            "item": "利用大模型检查汇报语气与专业度",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "大模型判定报告内容过于口语化、未明确说明车牌属性或缺乏专业度"
        })

    # Save Results
    with open(os.path.join(workspace_dir, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    target_workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(target_workspace)
