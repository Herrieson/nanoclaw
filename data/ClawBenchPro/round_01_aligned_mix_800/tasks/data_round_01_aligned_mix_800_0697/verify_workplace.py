import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，关闭 SSL 验证
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
    report_dir = os.path.join(workspace, "pta_report")
    
    total_score = 0
    details = []

    # 1. 验证目标文件夹是否存在
    if os.path.isdir(report_dir):
        details.append({
            "item": "检查报告目录是否存在", 
            "score": 20, 
            "max_score": 20, 
            "passed": True, 
            "reason": "目录 pta_report 存在"
        })
        total_score += 20
    else:
        details.append({
            "item": "检查报告目录是否存在", 
            "score": 0, 
            "max_score": 20, 
            "passed": False, 
            "reason": "目录 pta_report 不存在"
        })

    # 2. 验证目录下是否生成了报告文件并提取内容
    report_content = ""
    if os.path.isdir(report_dir):
        files = os.listdir(report_dir)
        if files:
            details.append({
                "item": "检查目录中是否包含报告文件", 
                "score": 10, 
                "max_score": 10, 
                "passed": True, 
                "reason": "成功在 pta_report 目录下发现文件"
            })
            total_score += 10
            
            # 读取所有文件（防御 Agent 把报告拆分）
            for f_name in files:
                file_path = os.path.join(report_dir, f_name)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as fp:
                            report_content += fp.read() + "\n"
                    except:
                        pass
        else:
            details.append({
                "item": "检查目录中是否包含报告文件", 
                "score": 0, 
                "max_score": 10, 
                "passed": False, 
                "reason": "pta_report 目录为空，未找到报告文件"
            })

    # 3. 使用 LLM 验证非结构化的报告内容
    if report_content.strip():
        # A. 验证未交作业的学生名单
        prompt_missing = (
            "Read the provided report. Determine if it correctly identifies EXACTLY 'Ethan' and 'Fiona' "
            "as the students who completely skipped or missed the assignment. "
            "It MUST NOT claim that 'Charlie' or 'George' missed the assignment, because they submitted logs "
            "(even if they were invasive weeds). Does the report correctly identify only Ethan and Fiona as missing?"
        )
        if llm_judge_content(prompt_missing, report_content):
            details.append({
                "item": "验证未提交作业的学生名单", 
                "score": 35, 
                "max_score": 35, 
                "passed": True, 
                "reason": "报告准确指出了未提交作业的学生是 Ethan 和 Fiona，未误判其他提交了入侵植物的学生"
            })
            total_score += 35
        else:
            details.append({
                "item": "验证未提交作业的学生名单", 
                "score": 0, 
                "max_score": 35, 
                "passed": False, 
                "reason": "大模型判定报告中遗漏了 Ethan/Fiona，或错误地将提交了入侵植物的学生（如Charlie/George）算作未交作业"
            })
            
        # B. 验证本土植物总生长量计算
        prompt_growth = (
            "Read the provided report. Does it explicitly state that the total combined growth of "
            "native plants is exactly 15 (or 15.0) inches?"
        )
        if llm_judge_content(prompt_growth, report_content):
            details.append({
                "item": "验证本土植物总生长量结果", 
                "score": 35, 
                "max_score": 35, 
                "passed": True, 
                "reason": "报告准确计算并提及了本土植物总生长量为 15.0 inches"
            })
            total_score += 35
        else:
            details.append({
                "item": "验证本土植物总生长量结果", 
                "score": 0, 
                "max_score": 35, 
                "passed": False, 
                "reason": "报告中给出的本土植物总生长量不正确（正确应为15.0），或未包含该数据"
            })
    else:
        # 没有报告内容，LLM判定直接判负
        details.append({"item": "验证未提交作业的学生名单", "score": 0, "max_score": 35, "passed": False, "reason": "报告无文本内容"})
        details.append({"item": "验证本土植物总生长量结果", "score": 0, "max_score": 35, "passed": False, "reason": "报告无文本内容"})

    # 将评测结果持久化
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
