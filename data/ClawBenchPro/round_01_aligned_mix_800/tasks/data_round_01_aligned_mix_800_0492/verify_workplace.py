import os
import sys
import json
import httpx
from openai import OpenAI

# 强制 API 规范：为符合规范保留LLM接口环境参数，虽然本题数据以强结构化为主，
# 但可用于扩展检测Agent是否擅自生成了要求外的冗余非结构化报告
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

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

def write_score(score, details):
    report = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    print(f"Verification finished. Total Score: {score}")

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "overdue_antiques_report.json")
    
    score = 0
    details = []

    # 1. 检查物理文件存在性 (10分)
    if os.path.exists(target_file):
        details.append({"item": "检查目标结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功找到 overdue_antiques_report.json"})
        score += 10
    else:
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 overdue_antiques_report.json"})
        write_score(score, details)
        return

    # 2. 验证原生 JSON 解析能力 (10分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "检查文件是否为合法JSON格式", "score": 10, "max_score": 10, "passed": True, "reason": "文件解析通过"})
        score += 10
    except Exception as e:
        details.append({"item": "检查文件是否为合法JSON格式", "score": 0, "max_score": 10, "passed": False, "reason": f"非合法 JSON，解析错误：{e}"})
        write_score(score, details)
        return

    # 3. 校验数据格式与结构容错解析 (20分)
    students_list = None
    total_cost = None

    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list) and all(isinstance(i, str) for i in v):
                students_list = v
            elif isinstance(v, (int, float)):
                total_cost = float(v)
            elif isinstance(v, str):
                # 容错提取：万一 Agent 返回了带着货币符号的字符串如 "$6,550.50"
                try:
                    clean_v = v.replace("$", "").replace(",", "").strip()
                    total_cost = float(clean_v)
                except ValueError:
                    pass

    if students_list is not None and total_cost is not None:
        details.append({"item": "检查JSON结构完整性", "score": 20, "max_score": 20, "passed": True, "reason": "包含合法格式的学生名单列表与数值型金额字段"})
        score += 20
    else:
        details.append({"item": "检查JSON结构完整性", "score": 0, "max_score": 20, "passed": False, "reason": "缺失学生列表(需为字符串列表)或金额字段(需可被解析为数值)"})
        students_list = students_list or []
        total_cost = total_cost or 0.0

    # 4. 学生名单精准核对 (30分，严查幻觉与误判)
    expected_students = {"Alice Vance", "David Smith", "Frank Castle"}
    # Agent 返回的数据可能存在重复，按题目要求去重处理
    actual_students = {str(s).strip() for s in students_list}
    
    correct_hits = expected_students.intersection(actual_students)
    false_positives = actual_students.difference(expected_students)
    
    if len(correct_hits) == 3 and len(false_positives) == 0:
        student_score = 30
        student_reason = "学生名单完美命中，无遗漏且未混入已经归还/未逾期/非受限的人员。"
    else:
        # 每个正确的给 10 分，每个错误的(幻觉/错误拦截)扣 10 分
        calc_score = len(correct_hits) * 10 - len(false_positives) * 10
        student_score = max(0, calc_score)
        student_reason = f"命中正确人员: {list(correct_hits)}。多余/错误人员(扣分): {list(false_positives)}。"

    details.append({"item": "检查受罚学生名单的精准性", "score": student_score, "max_score": 30, "passed": student_score == 30, "reason": student_reason})
    score += student_score

    # 5. 重置金额计算结果核对 (30分)
    expected_cost = 6550.50
    if abs(total_cost - expected_cost) < 0.01:
        details.append({"item": "检查最终重置成本准确性", "score": 30, "max_score": 30, "passed": True, "reason": "精准得出 6550.50，证明 CSV 清洗与金额加总逻辑完全正确。"})
        score += 30
    else:
        details.append({"item": "检查最终重置成本准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"数值计算错误。预期为 6550.50，实际拿到 {total_cost}。可能是 CSV 清洗失败或过滤逻辑遗漏。"})

    write_score(score, details)

if __name__ == "__main__":
    verify()
