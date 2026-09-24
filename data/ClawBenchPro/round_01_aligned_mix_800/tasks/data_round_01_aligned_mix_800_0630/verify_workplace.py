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

def extract_students_from_json(data):
    """Recursively search for students and their numbers in JSON structure"""
    results = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(k, str) and k in ["Luka Kovac", "Ana Horvat", "Marko Vidovic", "Petra Maric", "Ivan Peric"]:
                if isinstance(v, (int, float)):
                    results[k] = v
                elif isinstance(v, dict):
                    # Look for average or score
                    for sub_k, sub_v in v.items():
                        if isinstance(sub_v, (int, float)):
                            results[k] = sub_v
            else:
                results.update(extract_students_from_json(v))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                name = item.get("name", item.get("student", item.get("Name", "")))
                if name in ["Luka Kovac", "Ana Horvat", "Marko Vidovic", "Petra Maric", "Ivan Peric"]:
                    score = item.get("average", item.get("score", item.get("mean", None)))
                    if score is not None:
                        results[name] = score
                results.update(extract_students_from_json(item))
    return results

def get_needs_attention_flags(data):
    """Find out if any student is flagged for 'Needs Attention'"""
    str_data = json.dumps(data, ensure_ascii=False).lower()
    return "needs attention" in str_data or "attention" in str_data

def verify_workplace(workspace_path):
    score_details = []
    total_score = 0
    
    conf_dir = os.path.join(workspace_path, "conference_materials")
    final_grades_path = os.path.join(conf_dir, "final_grades.json")
    anomaly_report_path = os.path.join(conf_dir, "anomaly_report.txt")
    
    # 1. 检查目录 (10分)
    if os.path.isdir(conf_dir):
        score_details.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "conference_materials 目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "conference_materials 目录缺失"})
        
    # 2. 检查 JSON 报告是否存在及格式 (15分)
    json_data = None
    if os.path.isfile(final_grades_path):
        try:
            with open(final_grades_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            score_details.append({"item": "检查 final_grades.json 格式合法性", "score": 15, "max_score": 15, "passed": True, "reason": "JSON格式完全合法"})
            total_score += 15
        except Exception as e:
            score_details.append({"item": "检查 final_grades.json 格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"解析失败或不是合法的JSON: {e}"})
    else:
        score_details.append({"item": "检查 final_grades.json 格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": "文件缺失"})

    # 3. 检查异常报告是否存在 (10分)
    anomaly_text = ""
    if os.path.isfile(anomaly_report_path):
        with open(anomaly_report_path, "r", encoding="utf-8") as f:
            anomaly_text = f.read()
        score_details.append({"item": "检查 anomaly_report.txt 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 anomaly_report.txt 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})

    # 4. JSON 数据准确性：包含的名单与成绩 (30分)
    if json_data is not None:
        expected_scores = {
            "Luka Kovac": 90,  # (92+88)/2
            "Ana Horvat": 79,  # (76+82)/2
            "Marko Vidovic": 90, # A=95, B=85 -> 90
            "Petra Maric": 70, # C=75, D=65 -> 70
            "Ivan Peric": 90 # B=85, A=95 -> 90
        }
        
        extracted_students = extract_students_from_json(json_data)
        
        # 检查是否有多余的无关人员
        str_data = json.dumps(json_data, ensure_ascii=False)
        if "Unknown Entity" in str_data or "Stranger danger" in str_data:
            score_details.append({"item": "成绩单不可包含异常学生", "score": 0, "max_score": 10, "passed": False, "reason": "最终报告中包含了未在花名册中的异常学生，严厉扣分"})
        else:
            score_details.append({"item": "成绩单不可包含异常学生", "score": 10, "max_score": 10, "passed": True, "reason": "干净的数据，没有异常名单混入"})
            total_score += 10
            
        correct_counts = 0
        for name, exp_score in expected_scores.items():
            if name in extracted_students and abs(extracted_students[name] - exp_score) < 0.1:
                correct_counts += 1
                
        calc_score = correct_counts * 4 # 每人4分，最高20分
        if calc_score == 20:
            score_details.append({"item": "成绩平均分计算准确性", "score": 20, "max_score": 20, "passed": True, "reason": "5名学生平均分全部精准计算"})
            total_score += 20
        else:
            score_details.append({"item": "成绩平均分计算准确性", "score": calc_score, "max_score": 20, "passed": False, "reason": f"算对了 {correct_counts}/5 个学生的成绩"})
            total_score += calc_score
    else:
        score_details.append({"item": "成绩单不可包含异常学生", "score": 0, "max_score": 10, "passed": False, "reason": "无法读取 JSON"})
        score_details.append({"item": "成绩平均分计算准确性", "score": 0, "max_score": 20, "passed": False, "reason": "无法读取 JSON"})

    # 5. JSON 标志位检查 (10分)
    if json_data is not None:
        has_flag = get_needs_attention_flags(json_data)
        if has_flag:
            score_details.append({"item": "需要关注标记准确性", "score": 0, "max_score": 10, "passed": False, "reason": "平均分均 >= 70，无需任何'Needs Attention'标记，出现幻觉或计算错误"})
        else:
            score_details.append({"item": "需要关注标记准确性", "score": 10, "max_score": 10, "passed": True, "reason": "正确处理了 rubric (无学生严格低于 70，没有乱打标记)"})
            total_score += 10
    else:
        score_details.append({"item": "需要关注标记准确性", "score": 0, "max_score": 10, "passed": False, "reason": "无法读取 JSON"})
            
    # 6. LLM 语义检测异常报告 (25分)
    if anomaly_text:
        prompt = "Does the following text report accurately mention both 'Unknown Entity' and 'Stranger danger' as the unexpected/anomalous students that need to be excluded or highlighted? It should not invent or include official students."
        is_correct = llm_judge_content(prompt, anomaly_text)
        if is_correct:
            score_details.append({"item": "利用大模型检查异常报告内容", "score": 25, "max_score": 25, "passed": True, "reason": "准确识别并列出了两名异常学生"})
            total_score += 25
        else:
            score_details.append({"item": "利用大模型检查异常报告内容", "score": 0, "max_score": 25, "passed": False, "reason": "未能准确指出 Unknown Entity 和 Stranger danger 两名异常情况，或包含了错误信息"})
    else:
        score_details.append({"item": "利用大模型检查异常报告内容", "score": 0, "max_score": 25, "passed": False, "reason": "异常报告不存在"})
        
    with open(os.path.join(workspace_path, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
