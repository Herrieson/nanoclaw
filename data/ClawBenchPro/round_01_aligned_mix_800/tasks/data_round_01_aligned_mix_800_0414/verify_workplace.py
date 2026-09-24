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

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    escalation_dir = os.path.join(workspace, "escalation_report")
    
    score_details = []
    total_score = 0
    
    # 1. 目录结构检测
    dir_exists = os.path.isdir(escalation_dir)
    if dir_exists:
        score_details.append({"item": "Check if 'escalation_report' directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory 'escalation_report' found."})
        total_score += 10
    else:
        score_details.append({"item": "Check if 'escalation_report' directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'escalation_report' missing."})
    
    # 2. 读取报告文件
    report_content = ""
    if dir_exists:
        files = [f for f in os.listdir(escalation_dir) if os.path.isfile(os.path.join(escalation_dir, f))]
        if files:
            score_details.append({"item": "Check if report file is generated", "score": 10, "max_score": 10, "passed": True, "reason": f"Found file(s): {', '.join(files)}"})
            total_score += 10
            # 整合所有文本用于非结构化分析
            for file in files:
                with open(os.path.join(escalation_dir, file), 'r', encoding='utf-8', errors='ignore') as f:
                    report_content += f.read() + "\n\n"
        else:
            score_details.append({"item": "Check if report file is generated", "score": 0, "max_score": 10, "passed": False, "reason": "Directory exists but is empty."})
    else:
        score_details.append({"item": "Check if report file is generated", "score": 0, "max_score": 10, "passed": False, "reason": "Directory missing, no files to check."})
        
    # 如果没有内容，直接结束后续验证
    if not report_content.strip():
        score_details.append({"item": "Validating report content for required cases", "score": 0, "max_score": 50, "passed": False, "reason": "No report content found."})
        score_details.append({"item": "Checking for decoy contamination", "score": 0, "max_score": 20, "passed": False, "reason": "No report content found."})
        score_details.append({"item": "Professional tone check", "score": 0, "max_score": 10, "passed": False, "reason": "No report content found."})
    else:
        # 3. Valid Cases 检测 (大模型语义判断非结构化文本的准确覆盖率)
        valid_cases = [
            ("Marcus Vance", "Fake plastic garbage. No refund given."),
            ("Sarah Jenkins", "Broken ceramic upon arrival. Manager refused to help."),
            ("David Kim", "The 'authentic' rug is synthetic. Absolute scam."),
            ("Chloe Adams", "Never received the item, but ticket marked closed with no refund."),
            ("Marcus Vance", "The carving was hollow wood, not solid. Terrible.")
        ]
        
        cases_score = 0
        passed_cases = []
        failed_cases = []
        for manager, complaint in valid_cases:
            prompt = f"Does the following report explicitly state that manager '{manager}' was involved with a complaint matching the meaning of '{complaint}'?"
            if llm_judge_content(prompt, report_content):
                cases_score += 10
                passed_cases.append(manager)
            else:
                failed_cases.append(manager)
                
        cases_passed = (cases_score == 50)
        score_details.append({
            "item": "Validating report content for required cases", 
            "score": cases_score, 
            "max_score": 50, 
            "passed": cases_passed, 
            "reason": f"Found {len(passed_cases)}/5 valid cases. Missing: {failed_cases}."
        })
        total_score += cases_score
        
        # 4. Decoy 污染检测 (严厉扣分项，测试Agent是否精确处理了0退款、关闭状态、匹配代号等)
        decoy_prompt = "Does the report mistakenly include ANY complaints related to 'T-shirt size wrong', 'Box dented', or 'Still waiting'?"
        has_decoy = llm_judge_content(decoy_prompt, report_content)
        if has_decoy:
            score_details.append({"item": "Checking for decoy contamination", "score": 0, "max_score": 20, "passed": False, "reason": "Report contains decoy/invalid complaints (e.g. wrong product line, refunded items, or open status). Logic failed."})
        else:
            score_details.append({"item": "Checking for decoy contamination", "score": 20, "max_score": 20, "passed": True, "reason": "No decoys found. The parsing logic is perfectly strict."})
            total_score += 20
            
        # 5. Tone & Structure
        tone_prompt = "Is this report written in a professional, urgent tone suitable for a high-level escalation to a director, avoiding casual language?"
        has_tone = llm_judge_content(tone_prompt, report_content)
        if has_tone:
            score_details.append({"item": "Professional tone check", "score": 10, "max_score": 10, "passed": True, "reason": "Tone is professional and urgent."})
            total_score += 10
        else:
            score_details.append({"item": "Professional tone check", "score": 0, "max_score": 10, "passed": False, "reason": "Tone is too casual or lacks structural professionalism."})

    # 输出结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify_workplace()
