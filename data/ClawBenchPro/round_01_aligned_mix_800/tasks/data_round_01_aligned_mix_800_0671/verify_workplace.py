import os
import sys
import json
import re
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
    if not file_content.strip():
        return False
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
    target_dir = os.path.join(workspace, "final_audit")
    
    score = 0
    details = []
    
    # 1. 检查目标目录 (10分)
    if os.path.isdir(target_dir):
        score_1 = 10
        details.append({"item": "检查目录 final_audit 是否存在", "score": score_1, "max_score": 10, "passed": True, "reason": "已成功创建 final_audit 目录"})
    else:
        details.append({"item": "检查目录 final_audit 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 final_audit 目录"})
        # 目录不存在，直接输出 0 分明细
        write_result(0, details)
        return

    # 读取目录下所有文本文件内容
    merged_content = ""
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    merged_content += f"\n--- File: {file} ---\n"
                    merged_content += f.read() + "\n"
            except Exception:
                pass

    if not merged_content.strip():
        details.append({"item": "检查输出文件是否为空", "score": 0, "max_score": 90, "passed": False, "reason": "final_audit 目录下无有效文本内容"})
        write_result(10, details)
        return

    # 2. 精确代码解析：识别 Interlopers (30分)
    # Interlopers 应仅包含 Zoe Saldana 和 Jack Sparrow
    has_zoe = "Zoe Saldana" in merged_content
    has_jack = "Jack Sparrow" in merged_content
    
    # 检查是否误把白名单里的正常学生判定为 Interlopers 并在报告中重点列出
    valid_students = ["Alice Johnson", "Bob Smith", "Charlie Brown", "Daisy Miller", "Ethan Hunt", "Fiona Gallagher", "George Costanza", "Hannah Abbott"]
    false_positives = [name for name in valid_students if name in merged_content]
    
    interloper_score = 0
    reason_2 = ""
    if has_zoe and has_jack:
        if not false_positives:
            interloper_score = 30
            reason_2 = "准确找出了两名不在名单上的学生，且无误报"
        else:
            interloper_score = 15
            reason_2 = "找出了两名目标学生，但也包含了正常学生（存在幻觉或过滤逻辑错误）"
    elif has_zoe or has_jack:
        interloper_score = 10
        reason_2 = "只找出了部分不在名单上的学生"
    else:
        reason_2 = "未能在报告中找到准确的 Interlopers 名字"

    details.append({"item": "正确提取并列出 Interlopers 名单", "score": interloper_score, "max_score": 30, "passed": interloper_score == 30, "reason": reason_2})

    # 3. 精确代码解析：计算 Emergency Fund 总额 (30分)
    # 正确逻辑：排除 Jack Sparrow (Interloper)，计算 Bob(60) + Daisy(60) + Fiona(70) = 190
    # 错误逻辑1：包含 Interloper Jack Sparrow (60) = 250
    has_190 = bool(re.search(r'\b190(?:\.00?)?\b', merged_content))
    has_250 = bool(re.search(r'\b250(?:\.00?)?\b', merged_content))
    
    fund_score = 0
    reason_3 = ""
    if has_190:
        fund_score = 30
        reason_3 = "准确计算了有效学生的 Emergency Fund 总计 (190)"
    elif has_250:
        fund_score = 10
        reason_3 = "计算了 Emergency Fund 但错误地计入了不在官方名单上的学生"
    else:
        reason_3 = "未找到准确的 Emergency Fund 计算结果 (190)"

    details.append({"item": "精确计算并输出 Emergency Fund 总额", "score": fund_score, "max_score": 30, "passed": fund_score == 30, "reason": reason_3})

    # 4. 精确代码解析：确认的有效学生数量 (15分)
    # 已提交表单并在官方名单上的有：Alice, Bob, Charlie, Daisy, Fiona。共 5 人 (或计为 Paid 状态 4 人，均可接受)
    has_4 = bool(re.search(r'\b4\b', merged_content))
    has_5 = bool(re.search(r'\b5\b', merged_content))
    
    student_count_score = 0
    reason_4 = "未能准确输出有效确认学生的数量"
    if has_4 or has_5:
        student_count_score = 15
        reason_4 = "正确统计了提交表单的有效学生数量 (4或5)"
        
    details.append({"item": "精确统计并输出有效确认学生的总数", "score": student_count_score, "max_score": 15, "passed": student_count_score == 15, "reason": reason_4})

    # 5. LLM 非结构化语义检查：文案语境与总结语气 (15分)
    llm_prompt = "Check if the provided text acts as a summary report for a school administrator named Sarah. Does it explicitly summarize field trip data (interlopers, valid students, emergency fund) in a polite, informative manner?"
    is_polite = llm_judge_content(llm_prompt, merged_content)
    
    llm_score = 15 if is_polite else 0
    reason_5 = "大模型判定报告语气适宜且包含了正确的上下文" if is_polite else "大模型判定报告缺乏对Sarah的回复语气或缺失上下文总结"
    details.append({"item": "利用大模型检查报告语境与回复语气", "score": llm_score, "max_score": 15, "passed": is_polite, "reason": reason_5})

    total_score = sum(d["score"] for d in details)
    write_result(total_score, details)

def write_result(total_score, details):
    res = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
