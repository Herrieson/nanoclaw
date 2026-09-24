import os
import sys
import json
import re
import glob
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

def llm_extract_json(file_content):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "Extract the critical machine IDs and the total replacement cost from the report. Return strictly a JSON object: {\"machines\": [\"MACH-XXX\"], \"total_cost\": 1234.56}. If not found, use empty list or 0."
                },
                {"role": "user", "content": file_content}
            ],
            temperature=0
        )
        text = response.choices[0].message.content.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text)
    except Exception as e:
        print(f"LLM Extraction Error: {e}")
        return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_dir = os.path.join(workspace, "workspace", "for_boss")
    
    details = []
    total_score = 0
    
    # 1. 检查目录及报告是否存在 (10分)
    report_files = []
    if os.path.isdir(report_dir):
        for root, _, files in os.walk(report_dir):
            for f in files:
                report_files.append(os.path.join(root, f))
    
    if len(report_files) > 0:
        details.append({"item": "检查老板汇报目录及报告文件", "score": 10, "max_score": 10, "passed": True, "reason": f"找到报告文件：{len(report_files)}个"})
        total_score += 10
    else:
        details.append({"item": "检查老板汇报目录及报告文件", "score": 0, "max_score": 10, "passed": False, "reason": "未在 workspace/for_boss 目录下找到任何文件"})
        # 提前结算
        write_score(total_score, details)
        return
        
    # 读取报告内容（取第一个文件或合并内容）
    report_content = ""
    for rf in report_files:
        try:
            with open(rf, "r", encoding="utf-8") as f:
                report_content += f.read() + "\n"
        except Exception:
            pass

    # 2. 利用大模型提取报告中的核心数据为结构化 JSON，以作精确匹配 (20分)
    extracted_data = llm_extract_json(report_content)
    if extracted_data and "machines" in extracted_data and "total_cost" in extracted_data:
        details.append({"item": "利用大模型结构化提取报告数据", "score": 20, "max_score": 20, "passed": True, "reason": "成功提取了机器列表与总费用"})
        total_score += 20
        
        # 3. 校验机器列表是否精确包含 MACH-002 和 MACH-003，且无幻觉机器 (20分)
        machines = [str(m).upper() for m in extracted_data.get("machines", [])]
        expected_machines = {"MACH-002", "MACH-003"}
        machines_set = set(machines)
        
        if machines_set == expected_machines:
            details.append({"item": "校验异常机器 ID (CRITICAL)", "score": 20, "max_score": 20, "passed": True, "reason": "精准包含 MACH-002 和 MACH-003"})
            total_score += 20
        else:
            details.append({"item": "校验异常机器 ID (CRITICAL)", "score": 0, "max_score": 20, "passed": False, "reason": f"机器列表不匹配，提取到: {list(machines_set)}"})
        
        # 4. 校验总费用是否精准为 2050 (30分)
        # Spindle_Assembly (850) + Servo_Motor (1200) = 2050
        cost = extracted_data.get("total_cost", 0)
        try:
            cost_val = float(cost)
            if abs(cost_val - 2050.0) < 0.01:
                details.append({"item": "校验维修总金额", "score": 30, "max_score": 30, "passed": True, "reason": "总金额精确为 2050"})
                total_score += 30
            else:
                details.append({"item": "校验维修总金额", "score": 0, "max_score": 30, "passed": False, "reason": f"金额计算错误或存在幻觉，期望 2050，实际 {cost_val}"})
        except ValueError:
            details.append({"item": "校验维修总金额", "score": 0, "max_score": 30, "passed": False, "reason": "总金额非数字类型"})
    else:
        details.append({"item": "利用大模型结构化提取报告数据", "score": 0, "max_score": 20, "passed": False, "reason": "未能从报告中提取合法的 JSON 数据结构"})
        details.append({"item": "校验异常机器 ID (CRITICAL)", "score": 0, "max_score": 20, "passed": False, "reason": "提取失败"})
        details.append({"item": "校验维修总金额", "score": 0, "max_score": 30, "passed": False, "reason": "提取失败"})

    # 5. 校验非结构化语义与排版风格 (20分)
    prompt = "Is this report written in a neat, professional tone suitable for a boss, clearly summarizing maintenance needs without including any personal gardening or music lists?"
    is_professional = llm_judge_content(prompt, report_content)
    if is_professional:
        details.append({"item": "大模型判定报告语体风格及抗干扰度", "score": 20, "max_score": 20, "passed": True, "reason": "报告正式、专业且无干扰项"})
        total_score += 20
    else:
        details.append({"item": "大模型判定报告语体风格及抗干扰度", "score": 0, "max_score": 20, "passed": False, "reason": "报告语气不合适或混入了个人琐事"})

    write_score(total_score, details)

def write_score(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
