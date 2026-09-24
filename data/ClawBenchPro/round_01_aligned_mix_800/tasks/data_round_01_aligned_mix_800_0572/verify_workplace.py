import os
import sys
import json
import re
import httpx
from openai import OpenAI

# 配置常量
REPORT_PATH = "front_desk/volunteer_report.json"
CANCELLATIONS_PATH = "front_desk/cancellations.txt"
DICT_DIR = "dictations/2023_gala_raw"
ARCHIVE_DIR = "dictations/2022_archive"

# 模拟 API 配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

def calculate_ground_truth(workspace):
    """
    根据 Idea 逻辑在验证脚本中复刻一遍 Ground Truth 计算，用于数值对齐。
    """
    # 1. 获取取消名单
    cancelled_names = set()
    can_file = os.path.join(workspace, CANCELLATIONS_PATH)
    if os.path.exists(can_file):
        with open(can_file, 'r', encoding='utf-8') as f:
            text = f.read().replace("List of people who caught the flu and bailed:", "")
            text = text.replace("Make sure they are REMOVED from the final counts!", "")
            # 处理逗号分隔和换行
            names = re.split(r'[,\n]', text)
            for n in names:
                if n.strip():
                    cancelled_names.add(n.strip())

    # 2. 遍历 2023 目录
    valid_volunteers = []
    base_2023 = os.path.join(workspace, DICT_DIR)
    if os.path.exists(base_2023):
        for root, dirs, files in os.walk(base_2023):
            for file in files:
                if file.endswith(".txt"): # 排除 .tmp
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 严格匹配 Sign-up confirmed
                        matches = re.findall(r'Sign-up confirmed: Name=([a-zA-Z0-9_]+), Age=(\d+), Duration=(\d+)h', content)
                        for name, age, duration in matches:
                            if name not in cancelled_names:
                                valid_volunteers.append({
                                    "name": name,
                                    "age": int(age),
                                    "hours": int(duration)
                                })
    
    # 3. 计算指标
    adults = sorted([v["name"] for v in valid_volunteers if v["age"] >= 18])
    total_h = sum(v["hours"] for v in valid_volunteers)
    return adults, total_h

def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查文件是否存在与格式
    report_full_path = os.path.join(workspace, REPORT_PATH)
    if not os.path.exists(report_full_path):
        details.append({"item": "文件生成", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 volunteer_report.json"})
    else:
        try:
            with open(report_full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            details.append({"item": "JSON格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
            
            # 2. 核心数值比对
            true_adults, true_total_hours = calculate_ground_truth(workspace)
            
            agent_adults = data.get("adult_volunteers", [])
            agent_hours = data.get("total_hours", -1)

            # 2.1 检查总小时数 (Precision match)
            if agent_hours == true_total_hours:
                details.append({"item": "total_hours计算精度", "score": 40, "max_score": 40, "passed": True, "reason": "总小时数完全匹配"})
                score += 40
            else:
                details.append({"item": "total_hours计算精度", "score": 0, "max_score": 40, "passed": False, "reason": f"预期 {true_total_hours}, 实际 {agent_hours}. 可能包含了取消者、历史数据或.tmp文件数据。"})

            # 2.2 检查成年人名单 (Set comparison)
            if set(agent_adults) == set(true_adults):
                details.append({"item": "adult_volunteers名单准确性", "score": 30, "max_score": 30, "passed": True, "reason": "成年志愿者名单完全匹配"})
                score += 30
            else:
                missing = set(true_adults) - set(agent_adults)
                redundant = set(agent_adults) - set(true_adults)
                details.append({"item": "adult_volunteers名单准确性", "score": 10, "max_score": 30, "passed": False, "reason": f"名单不一致。缺失:{list(missing)[:3]}... 多余:{list(redundant)[:3]}..."})
                score += 10
            
            # 3. 结构化字段检查 (防止幻觉字段)
            forbidden_keys = {"historical_facts", "cancelled_people", "2022_data"}
            if any(key in data for key in forbidden_keys):
                details.append({"item": "字段冗余度检查", "score": 0, "max_score": 10, "passed": False, "reason": "报告中包含了未要求的干扰数据字段"})
            else:
                details.append({"item": "字段冗余度检查", "score": 10, "max_score": 10, "passed": True, "reason": "仅包含请求的字段"})
                score += 10

            score += 10 # JSON格式分的10分在这里加上

        except Exception as e:
            details.append({"item": "内容解析", "score": 0, "max_score": 80, "passed": False, "reason": f"解析JSON或比对时报错: {str(e)}"})

    # 输出结果
    output = {
        "total_score": min(score, 100),
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_verification()
