import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# 配置常量
REPORT_PATH = "reports/floor_audit.json"
INVENTORY_CSV = "data/inventory.csv"
SCHEDULE_JSON = "data/weekend_shifts.json"

# Mock API 配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端
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
                {"role": "system", "content": "You are a strict retail audit assistant. Answer ONLY with 'YES' or 'NO'."},
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
    report_file = os.path.join(workspace, REPORT_PATH)
    
    score_details = []
    total_score = 0

    # 1. 基础文件存在性检查 (10分)
    if os.path.exists(report_file):
        score_details.append({"item": "检查报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 floor_audit.json 已生成"})
        total_score += 10
    else:
        score_details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "报告文件未找到"})
        # 如果文件不存在，直接生成结果并退出
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return

    # 2. 结构合法性检查 (10分)
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score_details.append({"item": "JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        return

    # 3. 错位商品 ID 识别精准度 (30分)
    # 根据业务逻辑：102(Auto), 104(Hardware), 106(Auto), 108(Hardware) 是错位的
    expected_ids = {"102", "104", "106", "108"}
    actual_ids = set(str(i) for i in data.get("misplaced_item_ids", []) or data.get("misplaced_items", []))
    
    if actual_ids == expected_ids:
        score_details.append({"item": "错位商品 ID 识别", "score": 30, "max_score": 30, "passed": True, "reason": "完全匹配所有非 Apparel 商品 ID"})
        total_score += 30
    elif expected_ids.issubset(actual_ids):
        score_details.append({"item": "错位商品 ID 识别", "score": 15, "max_score": 30, "passed": False, "reason": "包含了正确 ID 但存在多余项（幻觉）"})
    else:
        score_details.append({"item": "错位商品 ID 识别", "score": 0, "max_score": 30, "passed": False, "reason": f"匹配失败，期望 {expected_ids}"})

    # 4. 财务金额计算 (30分)
    # 计算逻辑：
    # 102: 5 * 15.00 = 75.00
    # 104: 4 * 12.50 = 50.00
    # 106: 2 * 20.00 = 40.00
    # 108: 1 * 30.00 = 30.00
    # Total = 75 + 50 + 40 + 30 = 195.00
    expected_total = 195.00
    actual_total = data.get("total_misplaced_value", 0)
    
    # 允许少量浮点误差
    if abs(float(actual_total) - expected_total) < 0.01:
        score_details.append({"item": "错位商品总价值计算", "score": 30, "max_score": 30, "passed": True, "reason": "金额 195.00 计算准确"})
        total_score += 30
    else:
        score_details.append({"item": "错位商品总价值计算", "score": 0, "max_score": 30, "passed": False, "reason": f"金额错误，期望 195.00，实际 {actual_total}"})

    # 5. 加班员工识别 (20分)
    # Mike: 9h, David: 12h, Tom: 9h (Sarah: 7, Jessica: 8, Emily: 5)
    expected_overtime = {"Mike", "David", "Tom"}
    actual_overtime = set(data.get("overtime_employees", []))
    
    if actual_overtime == expected_overtime:
        score_details.append({"item": "违规加班人员识别", "score": 20, "max_score": 20, "passed": True, "reason": "准确识别所有超过 8 小时的员工"})
        total_score += 20
    else:
        score_details.append({"item": "违规加班人员识别", "score": 0, "max_score": 20, "passed": False, "reason": f"识别错误，期望 {expected_overtime}"})

    # 写入最终结果
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(total_score), "details": score_details}, f, indent=2)

if __name__ == "__main__":
    run_verification()
