import os
import sys
import json
import csv
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
    total_score = 0
    details = []

    processed_dir = os.path.join(workspace, "processed")
    if os.path.isdir(processed_dir):
        total_score += 10
        details.append({"item": "检查目标输出目录", "score": 10, "max_score": 10, "passed": True, "reason": "processed 目录存在"})
    else:
        details.append({"item": "检查目标输出目录", "score": 0, "max_score": 10, "passed": False, "reason": "processed 目录不存在"})

    # 检查 CSV 文件
    csv_path = os.path.join(processed_dir, "daily_appointments.csv")
    csv_exists = os.path.isfile(csv_path)
    if csv_exists:
        total_score += 10
        details.append({"item": "检查CSV文件存在与否", "score": 10, "max_score": 10, "passed": True, "reason": "CSV 文件已成功创建"})
        
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # 解析出含有人员姓名的数据行（剔除潜在的纯表头行）
            data_rows = []
            all_names = ["john", "jane", "alice", "bob", "charlie", "eve", "gregory", "sarah", "tom"]
            for row in rows:
                row_str = " ".join(row).lower()
                if any(name in row_str for name in all_names):
                    data_rows.append(row_str)
            
            # 1. 检查数据条目数量
            if len(data_rows) == 6:
                total_score += 10
                details.append({"item": "检查CSV有效行数", "score": 10, "max_score": 10, "passed": True, "reason": "数据行数量准确(6条)"})
            else:
                details.append({"item": "检查CSV有效行数", "score": 0, "max_score": 10, "passed": False, "reason": f"数据行数错误，期望 6 条，实际解析到 {len(data_rows)} 条"})

            # 2. 检查是否完全去除了非 HR Programs 部门人员
            bad_names = ["jane", "charlie", "sarah"]
            has_bad_names = any(bad in row_str for bad in bad_names for row_str in data_rows)
            if not has_bad_names and len(data_rows) > 0:
                total_score += 10
                details.append({"item": "检查CSV过滤逻辑", "score": 10, "max_score": 10, "passed": True, "reason": "成功剔除了非 HR 部门（DMV, Parks）的无用记录"})
            else:
                details.append({"item": "检查CSV过滤逻辑", "score": 0, "max_score": 10, "passed": False, "reason": "CSV 混入了非相关部门访客或数据异常"})

            # 3. 检查数据的时间先后排序
            expected_order = ["john", "alice", "eve", "tom", "bob", "gregory"]
            actual_order = []
            for row_str in data_rows:
                for name in expected_order:
                    if name in row_str and name not in actual_order:
                        actual_order.append(name)
            
            if actual_order == expected_order:
                total_score += 20
                details.append({"item": "检查CSV时序排序", "score": 20, "max_score": 20, "passed": True, "reason": "所有数据严格按照实际时间先后进行升序排列，不受AM/PM与24小时制乱码影响"})
            else:
                details.append({"item": "检查CSV时序排序", "score": 0, "max_score": 20, "passed": False, "reason": f"排序失败或人员不全。实际抽取到的人员排序为: {actual_order}"})
                
        except Exception as e:
            details.append({"item": "解析CSV文件", "score": 0, "max_score": 50, "passed": False, "reason": f"文件损坏或格式非法: {e}"})
    else:
        details.append({"item": "检查CSV文件存在与否", "score": 0, "max_score": 10, "passed": False, "reason": "daily_appointments.csv 未被创建"})
        details.append({"item": "检查CSV有效行数", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在，略过"})
        details.append({"item": "检查CSV过滤逻辑", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在，略过"})
        details.append({"item": "检查CSV时序排序", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在，略过"})

    # 检查保险诉求 txt 文件
    txt_path = os.path.join(processed_dir, "insurance_complaints.txt")
    if os.path.isfile(txt_path):
        total_score += 10
        details.append({"item": "检查特定提取TXT文件", "score": 10, "max_score": 10, "passed": True, "reason": "insurance_complaints.txt 文件存在"})
        
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                txt_content = f.read()
            content_lower = txt_content.lower()
            
            # 精准抽取: Alice Jones, Eve Evans. 不应包含其他人
            required_names = ["alice jones", "eve evans"]
            banned_names = ["john doe", "bob brown", "gregory house", "tom clark", "jane smith", "charlie davis", "sarah connor"]
            
            has_required = all(name in content_lower for name in required_names)
            has_banned = any(name in content_lower for name in banned_names)
            
            if has_required and not has_banned:
                total_score += 15
                details.append({"item": "检查保险人员提取准确性", "score": 15, "max_score": 15, "passed": True, "reason": "严格只包含了有健康保险争议或诉求的指定人员"})
            else:
                details.append({"item": "检查保险人员提取准确性", "score": 0, "max_score": 15, "passed": False, "reason": "未能提取特定人员（或混入了未谈及保险事务的人员）"})

            # 调用LLM确保语义清晰、记录了具体理由且没废话
            llm_prompt = "The user requested a neat extraction of individuals with health insurance inquiries or disputes, including their names and the specific reasons/complaints. Does this text clearly list their names and their respective reasons in a natural, readable format, WITHOUT raw technical logs or unrelated extraneous information?"
            if llm_judge_content(llm_prompt, txt_content):
                total_score += 15
                details.append({"item": "利用大模型检查内容质量", "score": 15, "max_score": 15, "passed": True, "reason": "格式清晰，包含具体的申诉原因，无多余冗杂技术日志，满足Persona洁癖要求"})
            else:
                details.append({"item": "利用大模型检查内容质量", "score": 0, "max_score": 15, "passed": False, "reason": "大模型判定提取出的信息格式混乱、含有无关内容或未能有效描述人员的保险诉求原因"})
                
        except Exception as e:
            details.append({"item": "读取并解析TXT文本", "score": 0, "max_score": 30, "passed": False, "reason": f"无法读取文本内容: {e}"})
    else:
        details.append({"item": "检查特定提取TXT文件", "score": 0, "max_score": 10, "passed": False, "reason": "insurance_complaints.txt 未被创建"})
        details.append({"item": "检查保险人员提取准确性", "score": 0, "max_score": 15, "passed": False, "reason": "文件不存在，略过"})
        details.append({"item": "利用大模型检查内容质量", "score": 0, "max_score": 15, "passed": False, "reason": "文件不存在，略过"})

    # 输出结果
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
