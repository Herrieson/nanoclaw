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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_dir = os.path.join(workspace, "investigation_report")
    
    details = []
    total_score = 0
    
    # 1. 检查基础结构 (20分)
    has_dir = os.path.exists(report_dir) and os.path.isdir(report_dir)
    details.append({"item": "检查 investigation_report 目录", "score": 10 if has_dir else 0, "max_score": 10, "passed": has_dir, "reason": "报告目录存在" if has_dir else "报告目录缺失"})
    total_score += 10 if has_dir else 0
    
    list_content = ""
    summary_content = ""
    list_file_found = False
    summary_file_found = False

    if has_dir:
        for f in os.listdir(report_dir):
            fpath = os.path.join(report_dir, f)
            if not os.path.isfile(fpath): continue
            name = f.lower()
            if "list" in name or "suspicious" in name:
                list_file_found = True
                with open(fpath, "r", encoding="utf-8") as file:
                    list_content = file.read()
            elif "summary" in name or "stat" in name:
                summary_file_found = True
                with open(fpath, "r", encoding="utf-8") as file:
                    summary_content = file.read()
    
    details.append({
        "item": "检查是否生成了名单与摘要文件", 
        "score": (5 if list_file_found else 0) + (5 if summary_file_found else 0), 
        "max_score": 10, 
        "passed": list_file_found and summary_file_found, 
        "reason": f"名单文件:{list_file_found}, 摘要文件:{summary_file_found}"
    })
    total_score += (5 if list_file_found else 0) + (5 if summary_file_found else 0)

    # 2. 精准数据提取与校验 (50分)
    if list_content:
        # 寻找特定的 EXP-xxx
        found_exp3 = "EXP-003" in list_content
        found_exp4 = "EXP-004" in list_content
        found_exp7 = "EXP-007" in list_content
        
        details.append({"item": "识别规则2违规(不在白名单): EXP-003", "score": 15 if found_exp3 else 0, "max_score": 15, "passed": found_exp3, "reason": "准确抓出不在白名单的报销项"})
        total_score += 15 if found_exp3 else 0
        
        details.append({"item": "识别规则1违规(>5000且无产出): EXP-004", "score": 15 if found_exp4 else 0, "max_score": 15, "passed": found_exp4, "reason": "准确识别无产出的大额报销项"})
        total_score += 15 if found_exp4 else 0

        details.append({"item": "识别规则1违规(>5000且无产出): EXP-007", "score": 10 if found_exp7 else 0, "max_score": 10, "passed": found_exp7, "reason": "准确识别无产出的大额报销项"})
        total_score += 10 if found_exp7 else 0

        # 反向校验：不允许错杀合法记录
        false_positives = [m for m in ["EXP-001", "EXP-002", "EXP-005", "EXP-006"] if m in list_content]
        no_false_pos = len(false_positives) == 0
        details.append({"item": "无误报合法项目", "score": 10 if no_false_pos else 0, "max_score": 10, "passed": no_false_pos, "reason": "未误判合法报销记录" if no_false_pos else f"误杀了合法记录: {false_positives}"})
        total_score += 10 if no_false_pos else 0
    else:
        details.append({"item": "核心结果提取", "score": 0, "max_score": 50, "passed": False, "reason": "未找到对应的调查清单文件，无法验证核心报销ID"})

    # 3. LLM 语义校验 (30分)
    if summary_content:
        prompt1 = "Did the text explicitly identify 'Dr. Malicious' as an unauthorized faculty member or mention that they are not in the whitelist?"
        caught_malicious = llm_judge_content(prompt1, summary_content)
        details.append({"item": "摘要提及 Dr. Malicious 的违规本质", "score": 15 if caught_malicious else 0, "max_score": 15, "passed": caught_malicious, "reason": "大模型判定摘要明确演艺了白名单筛查结果"})
        total_score += 15 if caught_malicious else 0
        
        prompt2 = "Does the text adopt a highly professional, serious, and investigative tone suitable for an official academic misconduct investigation report?"
        good_tone = llm_judge_content(prompt2, summary_content)
        details.append({"item": "调查报告基调评估", "score": 15 if good_tone else 0, "max_score": 15, "passed": good_tone, "reason": "大模型判定文字具有严谨、严肃的学术调查属性"})
        total_score += 15 if good_tone else 0
    else:
        details.append({"item": "LLM 语义校验", "score": 0, "max_score": 30, "passed": False, "reason": "缺少摘要报告，无法进行语义评估"})

    # 写入最终得分
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
