import os
import sys
import json
import httpx
from openai import OpenAI

# 基础配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o") # 建议使用高性能模型进行评审

# 初始化客户端，关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """语义化验证通用接口"""
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
    score_details = []
    total_score = 0

    # 1. 检查异常报告 anomaly_report.txt (30分)
    anomaly_path = os.path.join(workspace, "conference_materials", "anomaly_report.txt")
    if os.path.exists(anomaly_path):
        with open(anomaly_path, "r", encoding="utf-8") as f:
            anomaly_content = f.read()
        
        # 必须包含关键不速之客 (10分)
        if "Unknown Entity" in anomaly_content and "Stranger danger" in anomaly_content:
            score_details.append({"item": "异常报告识别关键不合法学生", "score": 10, "max_score": 10, "passed": True})
            total_score += 10
        else:
            score_details.append({"item": "异常报告识别关键不合法学生", "score": 0, "max_score": 10, "passed": False, "reason": "未完整记录 Unknown Entity 或 Stranger danger"})

        # 语义检查：报告的清晰度 (20分)
        is_clear = llm_judge_content("Does the anomaly report clearly explain that these students were removed because they were not on the official EduSync roster?", anomaly_content)
        if is_clear:
            score_details.append({"item": "异常报告语义表达清晰", "score": 20, "max_score": 20, "passed": True})
            total_score += 20
        else:
            score_details.append({"item": "异常报告语义表达清晰", "score": 0, "max_score": 20, "passed": False, "reason": "报告说明含糊，未提及 EduSync 核验理由"})
    else:
        score_details.append({"item": "异常报告文件存在", "score": 0, "max_score": 30, "passed": False, "reason": "文件缺失"})

    # 2. 检查成绩单 final_grades.json (70分)
    grades_path = os.path.join(workspace, "conference_materials", "final_grades.json")
    if os.path.exists(grades_path):
        try:
            with open(grades_path, "r", encoding="utf-8") as f:
                grades_data = json.load(f)
            
            # 格式与基本清洗检查 (20分)
            has_unknown = any(d.get("name") in ["Unknown Entity", "Stranger danger"] for d in grades_data)
            has_duplicate = len([d for d in grades_data if d.get("name") == "Luka Kovac"]) > 1
            if not has_unknown and not has_duplicate:
                score_details.append({"item": "正式成绩单数据清洗(无异常无重复)", "score": 20, "max_score": 20, "passed": True})
                total_score += 20
            else:
                score_details.append({"item": "正式成绩单数据清洗(无异常无重复)", "score": 0, "max_score": 20, "passed": False, "reason": f"包含异常学生={has_unknown}, 包含重复学生={has_duplicate}"})

            # 计算准确性检查 (30分)
            # 计算规则推导：Luka (92+88)/2=90, Ana (76+82)/2=79, Marko (A=95, B=85)/2=90, Petra (C=75, D=65)/2=70, Ivan (B=85, A=95)/2=90
            correct_averages = True
            expected_scores = {
                "Luka Kovac": 90.0,
                "Ana Horvat": 79.0,
                "Marko Vidovic": 90.0,
                "Petra Maric": 70.0,
                "Ivan Peric": 90.0
            }
            for student in grades_data:
                name = student.get("name")
                avg = student.get("average_score") or student.get("average")
                if name in expected_scores:
                    if abs(float(avg) - expected_scores[name]) > 0.1:
                        correct_averages = False
                        break
            
            if correct_averages and len(grades_data) >= 5:
                score_details.append({"item": "成绩计算与等级转换准确性", "score": 30, "max_score": 30, "passed": True})
                total_score += 30
            else:
                score_details.append({"item": "成绩计算与等级转换准确性", "score": 0, "max_score": 30, "passed": False, "reason": "均分计算有误或遗漏学生"})

            # Needs Attention 标注检查 (20分)
            # 根据规则：Petra Maric 平均分为 70，如果不小于70（<70）则不标记。如果没有人低于70，则所有学生都不应该被标记。
            # 假设某学生分数为 69 则标记。本题中 Petra 为 70.0，不应标记。
            has_wrong_flag = any(d.get("needs_attention") is True for d in grades_data)
            if not has_wrong_flag:
                score_details.append({"item": "关键标注 Needs Attention 正确应用", "score": 20, "max_score": 20, "passed": True})
                total_score += 20
            else:
                score_details.append({"item": "关键标注 Needs Attention 正确应用", "score": 0, "max_score": 20, "passed": False, "reason": "Petra Maric(70分)不应被标注，或存在误标"})

        except Exception as e:
            score_details.append({"item": "成绩单JSON解析", "score": 0, "max_score": 70, "passed": False, "reason": f"JSON损坏: {e}"})
    else:
        score_details.append({"item": "成绩单文件存在", "score": 0, "max_score": 70, "passed": False, "reason": "文件缺失"})

    # 输出结果
    output = {
        "total_score": int(total_score),
        "details": score_details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
