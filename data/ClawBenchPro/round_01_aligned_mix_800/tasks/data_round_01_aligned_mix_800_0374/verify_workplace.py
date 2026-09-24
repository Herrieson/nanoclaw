import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------------------------------------------------------      
# 1. 环境配置与核心常量定义
# ----------------------------------------------------------------      
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 权限真值表 (基于 IAM Skill 逻辑)
AUTHORIZED_USERS = ["Siobhan O'Sullivan", "Liam Murphy", "Aisling Quinn"]
# 日志数据真值 (基于 env_builder.py)
# 授权用户工时: 
# Siobhan: 120 + 200 = 320
# Liam: 45 + 60 = 105
# Aisling: 30
# Total = 320 + 105 + 30 = 455
EXPECTED_BILLABLE_MINUTES = 455
# 非授权用户: John Doe, Jane Smith
EXPECTED_UNAUTHORIZED_USERS = ["John Doe", "Jane Smith"]

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
report_path = os.path.join(workspace, "audit_reports/final_audit.json")

# ----------------------------------------------------------------      
# 2. 辅助验证函数
# ----------------------------------------------------------------      
def get_score_details():
    return {
        "total_score": 0,
        "details": []
    }

def add_detail(res, item, score, max_score, passed, reason):
    res["details"].append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    res["total_score"] += score

# ----------------------------------------------------------------      
# 3. 验证逻辑开始
# ----------------------------------------------------------------      
def main():
    res = get_score_details()

    # 1. 检查文件是否存在 (10分)
    if os.path.exists(report_path):
        add_detail(res, "基础文件检查", 10, 10, True, "final_audit.json 已成功生成")
    else:
        add_detail(res, "基础文件检查", 0, 10, False, "未找到 audit_reports/final_audit.json")
        # 如果文件不存在，后续无法进行，直接输出
        with open("workplace_score.json", "w") as f:
            json.dump(res, f, indent=2)
        return

    # 2. 解析 JSON 格式 (10分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        add_detail(res, "JSON格式合法性", 10, 10, True, "JSON文件能够被标准库解析")
    except Exception as e:
        add_detail(res, "JSON格式合法性", 0, 10, False, f"JSON解析失败: {str(e)}")
        with open("workplace_score.json", "w") as f:
            json.dump(res, f, indent=2)
        return

    # 3. 验证非授权用户识别 (30分)
    # 要求：识别出 John Doe 和 Jane Smith，不能多也不能少
    found_unauthorized = [u.strip() for u in data.get("unauthorized_users", [])]
    # 使用集合对比，忽略顺序
    if set(found_unauthorized) == set(EXPECTED_UNAUTHORIZED_USERS):
        add_detail(res, "非授权用户识别", 30, 30, True, "精准识别出 John Doe 和 Jane Smith")
    elif any(u in found_unauthorized for u in EXPECTED_UNAUTHORIZED_USERS):
        add_detail(res, "非授权用户识别", 15, 30, False, f"部分识别正确。得到: {found_unauthorized}")
    else:
        add_detail(res, "非授权用户识别", 0, 30, False, "未能识别出正确的违规人员")

    # 4. 验证可计费工时计算 (40分) - 梯度给分
    total_minutes = data.get("total_billable_minutes")
    if total_minutes == EXPECTED_BILLABLE_MINUTES:
        add_detail(res, "计费工时精准度", 40, 40, True, f"工时计算准确: {EXPECTED_BILLABLE_MINUTES} 分钟")
    elif isinstance(total_minutes, (int, float)) and abs(total_minutes - EXPECTED_BILLABLE_MINUTES) <= 60:
        add_detail(res, "计费工时精准度", 20, 40, False, f"工时计算存在偏差，期望 {EXPECTED_BILLABLE_MINUTES}，得到 {total_minutes}")
    else:
        add_detail(res, "计费工时精准度", 0, 40, False, f"工时计算错误或缺失，得到: {total_minutes}")

    # 5. 检查是否存在伪造/幻觉数据 (10分)
    # 如果 JSON 里包含了 access_logs 之外的无关用户，说明可能产生了幻觉
    if "unauthorized_users" in data:
        hallucination = False
        for user in found_unauthorized:
            if user not in ["John Doe", "Jane Smith", "Siobhan O'Sullivan", "Liam Murphy", "Aisling Quinn"]:
                hallucination = True
                break
        if not hallucination:
            add_detail(res, "数据严谨性", 10, 10, True, "未发现名单外的幻觉数据")
        else:
            add_detail(res, "数据严谨性", 0, 10, False, "报告中包含日志中不存在的虚构人员")

    # 写入最终结果
    with open("workplace_score.json", "w") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
