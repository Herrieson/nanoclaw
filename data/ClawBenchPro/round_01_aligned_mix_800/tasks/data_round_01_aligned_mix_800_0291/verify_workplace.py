import os
import sys
import json
import httpx
import pandas as pd
from openai import OpenAI

# 配置环境
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
    """用于验证报告的总结性/描述性内容"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a senior structural engineer. Answer ONLY with 'YES' or 'NO'."},
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
    report_path = os.path.join(workspace, "export/stress_report.json")
    score = 0
    details = []

    # 1. 基础检查：目录与文件存在性 (10分)
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "检查报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 stress_report.json 已生成"})
    else:
        details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        # 核心文件缺失后续检查无法进行，直接输出
        save_results(score, details)
        return

    # 2. 结构化解析：Schema 合法性 (20分)
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score += 20
        details.append({"item": "JSON 格式合法性与解析", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 语法正确"})
    except Exception as e:
        details.append({"item": "JSON 格式合法性与解析", "score": 0, "max_score": 20, "passed": False, "reason": f"解析失败: {str(e)}"})
        save_results(score, details)
        return

    # 3. 核心计算验证：Peak Load 峰值载荷 (30分)
    # 注入点：1250.75 lbf, ID: TX-007
    expected_peak_load = 1250.75
    expected_peak_id = "TX-007"
    
    actual_peak_load = data.get("peak_load")
    actual_peak_id = data.get("peak_sensor_id") or data.get("peak_id")
    
    if actual_peak_load == expected_peak_load and str(actual_peak_id) == expected_peak_id:
        score += 30
        details.append({"item": "峰值载荷计算 (Peak Load)", "score": 30, "max_score": 30, "passed": True, "reason": f"精准匹配峰值 1250.75 lbf (TX-007)"})
    elif actual_peak_load == expected_peak_load:
        score += 15
        details.append({"item": "峰值载荷计算 (Peak Load)", "score": 15, "max_score": 30, "passed": False, "reason": "数值正确但 ID 匹配失败"})
    else:
        details.append({"item": "峰值载荷计算 (Peak Load)", "score": 0, "max_score": 30, "passed": False, "reason": f"数值不匹配，期望 {expected_peak_load}"})

    # 4. 逻辑过滤验证：阈值超标名单 (30分)
    # 注入点：TX-004 (5.3mm), TX-009 (6.1mm)
    expected_breaches = {"TX-004", "TX-009"}
    actual_breaches = set(data.get("flagged_sensors") or data.get("breached_sensors", []))
    
    if expected_breaches.issubset(actual_breaches) and len(actual_breaches) == 2:
        score += 30
        details.append({"item": "阈值超标过滤 (Deflection > 5.0mm)", "score": 30, "max_score": 30, "passed": True, "reason": "精准识别 TX-004 和 TX-009"})
    elif expected_breaches.intersection(actual_breaches):
        score += 15
        details.append({"item": "阈值超标过滤 (Deflection > 5.0mm)", "score": 15, "max_score": 30, "passed": False, "reason": "部分识别或包含多余干扰项"})
    else:
        details.append({"item": "阈值超标过滤 (Deflection > 5.0mm)", "score": 0, "max_score": 30, "passed": False, "reason": "未能识别超标传感器"})

    # 5. 抗干扰验证：忽略损坏文件 (10分)
    # 如果 Agent 汇报了 TX-001 等正常数据，且总数没有被 run_03_err.log 干扰
    prompt = "Based on the engineering report, does it correctly ignore the corrupted 'run_03_err.log' and focus only on valid telemetry?"
    if llm_judge_content(prompt, json.dumps(data)):
        score += 10
        details.append({"item": "数据清洗与抗干扰", "score": 10, "max_score": 10, "passed": True, "reason": "成功忽略损坏日志且未包含无效数据"})
    else:
        details.append({"item": "数据清洗与抗干扰", "score": 0, "max_score": 10, "passed": False, "reason": "报告中可能包含脏数据或受损坏文件误导"})

    save_results(score, details)

def save_results(score, details):
    output = {
        "total_score": int(score),
        "details": details
    }
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
