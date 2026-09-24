import os
import sys
import json
import httpx
import csv
import re
from openai import OpenAI

# 强制从环境变量获取 MOCK 信息
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """使用大模型判定非结构化文本的语义"""
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
    details = []
    total_score = 0
    
    report_dir = os.path.join(workspace, "archive_report")
    
    # 1. 检查物理目录是否存在 (10分)
    if os.path.isdir(report_dir):
        details.append({"item": "检查交付目录 archive_report 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "archive_report 目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查交付目录 archive_report 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 archive_report 目录"})
        return write_score(total_score, details)

    # 读取目录中的文件
    files_in_report = os.listdir(report_dir)
    
    # 2. 读取总结报告并利用 LLM 检查语义 (40分)
    summary_content = ""
    for f in files_in_report:
        if "summary" in f.lower() or f.endswith(".txt") or f.endswith(".md"):
            try:
                with open(os.path.join(report_dir, f), "r", encoding="utf-8") as file:
                    summary_content += file.read() + "\n"
            except:
                pass

    if summary_content:
        # 验证总费用 (基础费用 12.5*6 + 修复附加费 15.5 = 90.50)
        prompt_cost = "Does the text explicitly mention the final total cost of exactly $90.50 (or 90.5)?"
        if llm_judge_content(prompt_cost, summary_content):
            details.append({"item": "大模型语义检查 - 总预算统计准确性", "score": 20, "max_score": 20, "passed": True, "reason": "报告中给出了正确的总预算 $90.50"})
            total_score += 20
        else:
            details.append({"item": "大模型语义检查 - 总预算统计准确性", "score": 0, "max_score": 20, "passed": False, "reason": "未在报告中检测到准确的总费用 $90.50"})
            
        # 验证去重与统计反馈
        prompt_dups = "Does the text explicitly mention that there were 6 valid unique records, and that duplicates and invalid entries were filtered out?"
        if llm_judge_content(prompt_dups, summary_content):
            details.append({"item": "大模型语义检查 - 记录状态总结", "score": 20, "max_score": 20, "passed": True, "reason": "报告清晰地总结了去重逻辑并统计出6条有效记录"})
            total_score += 20
        else:
            details.append({"item": "大模型语义检查 - 记录状态总结", "score": 0, "max_score": 20, "passed": False, "reason": "未准确提到包含6条有效记录及其去重情况"})
    else:
        details.append({"item": "大模型语义检查 - 总结报告", "score": 0, "max_score": 40, "passed": False, "reason": "未找到可以被识别为 summary 的文本或 Markdown 文件"})

    # 3. 定位并严格解析结构化整合数据 (50分)
    consolidated_ids = set()
    valid_structure = False
    
    for f in files_in_report:
        f_path = os.path.join(report_dir, f)
        if f.endswith(".csv"):
            try:
                with open(f_path, "r", encoding="utf-8") as csvf:
                    reader = csv.reader(csvf)
                    for row in reader:
                        for cell in row:
                            if "ESP-" in cell:
                                match = re.search(r'ESP-\d{3}', cell)
                                if match: consolidated_ids.add(match.group())
                valid_structure = True
            except: pass
        elif f.endswith(".json"):
            try:
                with open(f_path, "r", encoding="utf-8") as jsonf:
                    data = json.dumps(json.load(jsonf))
                    consolidated_ids.update(re.findall(r'ESP-\d{3}', data))
                valid_structure = True
            except: pass

    if valid_structure:
        details.append({"item": "代码逻辑 - 结构化数据文件解析", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析了整合后的 CSV/JSON 结构化文件"})
        total_score += 10
    else:
        details.append({"item": "代码逻辑 - 结构化数据文件解析", "score": 0, "max_score": 10, "passed": False, "reason": "目录下缺少合法的 CSV/JSON 整合文件"})

    # 4. 精准核对有效书目去重结果 (40分)
    # 按照业务逻辑，ESP-003缺Title，一个缺ID，最终应该精准保留 6 条：
    expected_ids = {"ESP-001", "ESP-002", "ESP-004", "ESP-005", "ESP-006", "ESP-007"}
    
    if valid_structure and consolidated_ids:
        missing = expected_ids - consolidated_ids
        extra = consolidated_ids - expected_ids
        score_data = 40
        reason_parts = []
        
        if len(missing) == 0 and len(extra) == 0:
            reason_parts.append("数据条目完全正确，实现精准去重和错误剔除")
        else:
            if missing:
                penalty = len(missing) * 5
                score_data -= penalty
                reason_parts.append(f"遗漏了合法记录 {missing}，扣 {penalty} 分")
            if extra:
                penalty = len(extra) * 10  # 对混入脏数据/重复项进行重罚
                score_data -= penalty
                reason_parts.append(f"包含无效或冗余的错误记录 {extra}，扣 {penalty} 分")
                
        if score_data < 0: score_data = 0
            
        details.append({
            "item": "代码逻辑 - 核心清单 Call_Number 验证", 
            "score": score_data, 
            "max_score": 40, 
            "passed": score_data == 40, 
            "reason": "; ".join(reason_parts) if reason_parts else "完全匹配"
        })
        total_score += score_data
    else:
        details.append({"item": "代码逻辑 - 核心清单 Call_Number 验证", "score": 0, "max_score": 40, "passed": False, "reason": "无结构化书目数据可供验证"})

    write_score(total_score, details)

def write_score(total_score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
