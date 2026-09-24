import os
import sys
import json
import csv
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

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

def verify(workspace):
    details = []
    total_score = 0
    
    deliverables_dir = os.path.join(workspace, "deliverables")
    csv_file = os.path.join(deliverables_dir, "math_assessment_summary.csv")
    txt_file = os.path.join(deliverables_dir, "struggling_students.txt")
    
    # 1. 目录存在性 (10)
    if os.path.isdir(deliverables_dir):
        details.append({"item": "检查 deliverables 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=4)
        return

    # 2. CSV 存在与格式 (10)
    csv_data = {}
    csv_valid = False
    if os.path.isfile(csv_file):
        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                if len(header) >= 3:
                    for row in reader:
                        if len(row) >= 3:
                            name = row[0].strip().lower()
                            try:
                                time_spent = float(row[1].strip())
                                avg_score = float(row[2].strip())
                                csv_data[name] = {"time": time_spent, "score": avg_score}
                            except ValueError:
                                pass
                    details.append({"item": "检查 math_assessment_summary.csv 是否存在且格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "CSV 存在且列结构合法"})
                    total_score += 10
                    csv_valid = True
                else:
                    details.append({"item": "检查 math_assessment_summary.csv 是否存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "表头列数不足"})
        except Exception as e:
            details.append({"item": "检查 math_assessment_summary.csv 是否存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析报错: {e}"})
    else:
        details.append({"item": "检查 math_assessment_summary.csv 是否存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})

    # 3. CSV 数据准确性 (40)
    # 期望值:
    # Leo Rossi: time=55, score=82.5
    # Mia Wong: time=35, score=62.5
    # Robert Brown: time=50, score=95.0
    # Emily Chen: time=25, score=90.0
    # Chloe Smith: 必须不在里面 (没做 math)
    if csv_valid:
        # Chloe Smith
        if "chloe smith" not in csv_data:
            details.append({"item": "检查非数学模块的数据剔除情况", "score": 10, "max_score": 10, "passed": True, "reason": "成功剔除了没做数学题的 Chloe Smith"})
            total_score += 10
        else:
            details.append({"item": "检查非数学模块的数据剔除情况", "score": 0, "max_score": 10, "passed": False, "reason": "未能剔除 Chloe Smith，包含了错误学科数据"})
            
        # Leo Rossi
        if "leo rossi" in csv_data and csv_data["leo rossi"]["time"] == 55 and abs(csv_data["leo rossi"]["score"] - 82.5) < 0.1:
            details.append({"item": "计算 Leo Rossi 的多条混杂记录", "score": 10, "max_score": 10, "passed": True, "reason": "计算正确 (55分钟, 82.5分)"})
            total_score += 10
        else:
            details.append({"item": "计算 Leo Rossi 的多条混杂记录", "score": 0, "max_score": 10, "passed": False, "reason": "计算错误或记录缺失"})
            
        # Mia Wong
        if "mia wong" in csv_data and csv_data["mia wong"]["time"] == 35 and abs(csv_data["mia wong"]["score"] - 62.5) < 0.1:
            details.append({"item": "计算 Mia Wong 的多条混杂记录", "score": 10, "max_score": 10, "passed": True, "reason": "计算正确 (35分钟, 62.5分)"})
            total_score += 10
        else:
            details.append({"item": "计算 Mia Wong 的多条混杂记录", "score": 0, "max_score": 10, "passed": False, "reason": "计算错误或记录缺失"})
            
        # Robert & Emily (合并一项占 10 分)
        if "robert brown" in csv_data and csv_data["robert brown"]["time"] == 50 and csv_data["robert brown"]["score"] == 95.0 and \
           "emily chen" in csv_data and csv_data["emily chen"]["time"] == 25 and csv_data["emily chen"]["score"] == 90.0:
            details.append({"item": "计算其余正常学生的表现", "score": 10, "max_score": 10, "passed": True, "reason": "Robert 和 Emily 数据正确"})
            total_score += 10
        else:
            details.append({"item": "计算其余正常学生的表现", "score": 0, "max_score": 10, "passed": False, "reason": "Robert 或 Emily 数据错误"})
    else:
        details.append({"item": "CSV 数据准确性", "score": 0, "max_score": 40, "passed": False, "reason": "CSV 验证失败，跳过数据校验"})

    # 4. Struggling Students TXT 验证 (40)
    # Expected: Mia Wong (avg score < 70) and Emily Chen (time < 30)
    if os.path.isfile(txt_file):
        details.append({"item": "检查 struggling_students.txt 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
        
        with open(txt_file, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
        # 检测 Mia Wong 和 Emily Chen
        if "mia wong" in content and "emily chen" in content:
            details.append({"item": "判断是否找出了所有困难学生", "score": 15, "max_score": 15, "passed": True, "reason": "成功找到 Mia Wong 和 Emily Chen"})
            total_score += 15
        else:
            details.append({"item": "判断是否找出了所有困难学生", "score": 0, "max_score": 15, "passed": False, "reason": "遗漏了应被标记的学生"})
            
        # 严查幻觉：不能包含 Leo Rossi 或 Robert Brown
        if "leo rossi" not in content and "robert brown" not in content and "chloe smith" not in content:
            details.append({"item": "检查困难名单是否包含幻觉/误伤", "score": 15, "max_score": 15, "passed": True, "reason": "名单精确，没有误伤正常学生"})
            total_score += 15
        else:
            details.append({"item": "检查困难名单是否包含幻觉/误伤", "score": 0, "max_score": 15, "passed": False, "reason": "大模型幻觉：包含了不符合困难标准的学生"})
    else:
        details.append({"item": "检查 struggling_students.txt 文件是否存在及内容", "score": 0, "max_score": 40, "passed": False, "reason": "TXT 文件不存在"})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=4)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
