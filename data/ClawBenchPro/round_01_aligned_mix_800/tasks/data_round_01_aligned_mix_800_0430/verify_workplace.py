import os
import sys
import json
import csv
import re
import httpx
from openai import OpenAI

# 配置常量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化 LLM 客户端
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

def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 路径定义
    target_dir = os.path.join(workspace, "conference_materials")
    anomaly_file = os.path.join(target_dir, "anomaly_report.txt")
    final_json = os.path.join(target_dir, "final_grades.json")

    # 1. 检查目录和文件存在性 (10分)
    if os.path.exists(target_dir):
        score += 5
        details.append({"item": "检查结果目录是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "目录 conference_materials 存在"})
        
        files_exist = os.path.exists(anomaly_file) and os.path.exists(final_json)
        if files_exist:
            score += 5
            details.append({"item": "检查结果文件是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "anomaly_report.txt 和 final_grades.json 均存在"})
        else:
            details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "缺少必要的结果文件"})
    else:
        details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "找不到目录 conference_materials"})

    # 2. 检查 anomaly_report.txt 的准确性 (30分)
    # 根据 env_builder: Ghost IDs (STU-9900~9919) + Withdrawn (STU-1200~1229)
    # 且必须是按字母顺序排列
    if os.path.exists(anomaly_file):
        try:
            with open(anomaly_file, "r") as f:
                anomalies = [line.strip() for line in f if line.strip()]
            
            # 检查排序
            is_sorted = anomalies == sorted(anomalies)
            
            # 检查关键 ID 覆盖（至少包含 9900 段和 1200 段）
            has_ghost = any(a.startswith("STU-99") for a in anomalies)
            has_withdrawn = any(a.startswith("STU-12") for a in anomalies)
            
            if is_sorted and has_ghost and has_withdrawn:
                score += 30
                details.append({"item": "异常报告内容与排序", "score": 30, "max_score": 30, "passed": True, "reason": "ID列表排序正确，且包含幽灵ID与退学ID"})
            elif is_sorted:
                score += 15
                details.append({"item": "异常报告内容与排序", "score": 15, "max_score": 30, "passed": False, "reason": "列表已排序但ID覆盖不全"})
            else:
                score += 10
                details.append({"item": "异常报告内容与排序", "score": 10, "max_score": 30, "passed": False, "reason": "列表未排序或内容错误"})
        except Exception as e:
            details.append({"item": "异常报告读取错误", "score": 0, "max_score": 30, "passed": False, "reason": str(e)})

    # 3. 检查 final_grades.json 的格式与关键逻辑 (60分)
    if os.path.exists(final_json):
        try:
            with open(final_json, "r") as f:
                data = json.load(f)
            
            # 3.1 检查是否包含 active 学生 (STU-1300+)
            sample_active_id = "STU-1300"
            if sample_active_id in data:
                score += 15
                details.append({"item": "JSON包含有效学生", "score": 15, "max_score": 15, "passed": True, "reason": f"成功找到活动学生 {sample_active_id}"})
            else:
                details.append({"item": "JSON包含有效学生", "score": 0, "max_score": 15, "passed": False, "reason": "未找到活动学生记录"})

            # 3.2 检查是否排除了垃圾数据 (关键: 不应包含 _backup/_ignore 数据)
            # 通过检查数值精度或随机抽样判断，但这比较难，我们使用 LLM 辅助判断
            prompt = "The file is a student grade report. Does it follow the structure {ID: {name: str, average: float, flag: str}} and are the averages reasonable (not containing obviously huge numbers from multiple backup contaminations)?"
            if llm_judge_content(prompt, json.dumps(data)[:2000]):
                score += 15
                details.append({"item": "JSON结构与数值合理性", "score": 15, "max_score": 15, "passed": True, "reason": "LLM 判定结构符合要求且无明显数值异常"})
            else:
                details.append({"item": "JSON结构与数值合理性", "score": 0, "max_score": 15, "passed": False, "reason": "LLM 判定结构或数值异常"})

            # 3.3 验证判断阈值逻辑 (Avg < 68.0 -> Needs Attention)
            threshold_correct = True
            count_checked = 0
            for sid, info in data.items():
                avg = info.get("average", 0)
                flag = info.get("flag", "")
                if avg < 68.0:
                    if flag != "Needs Attention": threshold_correct = False
                else:
                    if flag != "OK": threshold_correct = False
                count_checked += 1
                if count_checked > 20: break # 抽样检查
            
            if threshold_correct and count_checked > 0:
                score += 20
                details.append({"item": "评分标准与Flag逻辑", "score": 20, "max_score": 20, "passed": True, "reason": "成功识别并应用了 < 68.0 的判定标准"})
            else:
                details.append({"item": "评分标准与Flag逻辑", "score": 0, "max_score": 20, "passed": False, "reason": "Flag判定标准错误或未找到评分标准"})

            # 3.4 检查是否包含非法 ID (Ghost/Withdrawn 不应在 final_grades 里)
            if not any(sid.startswith("STU-99") or sid.startswith("STU-12") for sid in data.keys()):
                score += 10
                details.append({"item": "数据隔离验证", "score": 10, "max_score": 10, "passed": True, "reason": "正式成绩单中没有包含异常 ID"})
            else:
                details.append({"item": "数据隔离验证", "score": 0, "max_score": 10, "passed": False, "reason": "正式成绩单中混入了幽灵或退学学生"})

        except Exception as e:
            details.append({"item": "JSON解析错误", "score": 0, "max_score": 60, "passed": False, "reason": str(e)})

    # 输出结果
    result = {
        "total_score": min(100, score),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    run_verification()
