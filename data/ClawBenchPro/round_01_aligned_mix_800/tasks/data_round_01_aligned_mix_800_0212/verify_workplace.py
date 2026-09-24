import os
import sys
import json
import httpx
from openai import OpenAI

# 配置常量
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
    """用于验证非结构化文本语义"""
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

    # 1. 检查目录与文件存在性 (10分)
    reports_dir = os.path.join(workspace, "reports")
    urgent_file = os.path.join(reports_dir, "urgent_care.txt")
    alfalfa_file = os.path.join(reports_dir, "total_alfalfa.txt")
    
    dir_exists = os.path.exists(reports_dir)
    urgent_exists = os.path.exists(urgent_file)
    alfalfa_exists = os.path.exists(alfalfa_file)

    score_dir = 10 if (dir_exists and urgent_exists and alfalfa_exists) else 0
    score_details.append({
        "item": "基础文件结构检查",
        "score": score_dir,
        "max_score": 10,
        "passed": score_dir == 10,
        "reason": "reports 目录及必要文件生成完整" if score_dir == 10 else "缺失 reports 目录或必要的结果文件"
    })
    total_score += score_dir

    # 2. 检查紧急护理列表 (40分) - 需包含 Cow-104 和 Horse-07
    if urgent_exists:
        try:
            with open(urgent_file, "r") as f:
                content = f.read().upper()
            
            has_cow = "COW-104" in content
            has_horse = "HORSE-07" in content
            # 严格排除干扰项 (Sheep-092, Sheep-099, Cow-105, Goat-12)
            has_noise = any(x in content for x in ["092", "105", "12", "099"])
            
            sub_score = 0
            if has_cow: sub_score += 20
            if has_horse: sub_score += 20
            if has_noise: sub_score -= 10 # 误报扣分
            
            sub_score = max(0, sub_score)
            score_details.append({
                "item": "动物健康风险识别 (Cow-104 & Horse-07)",
                "score": sub_score,
                "max_score": 40,
                "passed": sub_score >= 40,
                "reason": f"识别状态: Cow-104({'Found' if has_cow else 'Miss'}), Horse-07({'Found' if has_horse else 'Miss'}). 是否含干扰项: {has_noise}"
            })
            total_score += sub_score
        except Exception as e:
            score_details.append({"item": "动物健康风险识别", "score": 0, "max_score": 40, "passed": False, "reason": str(e)})

    # 3. 检查 Alfalfa 总量 (50分)
    # 根据 API 预期返回 (假定: Oct 1: 500 lbs, Oct 15: 1200 lbs, Oct 28: 300 lbs -> Total: 2000)
    # 此处假设 Mock API 在 Agent 调用时会返回具体值。由于环境脚本未给定 CSV，需看 Agent 调用 API 的逻辑。
    # 模拟标准答案：2000 (具体取决于 Cloud Agri Ledger API 的内部逻辑，此处设定为数值解析)
    if alfalfa_exists:
        try:
            with open(alfalfa_file, "r") as f:
                val_str = f.read().strip()
                # 提取数字
                import re
                numbers = re.findall(r"[-+]?\d*\.\d+|\d+", val_str)
                if numbers:
                    val = float(numbers[0])
                    # 验证逻辑：基于 Cloud API 返回的 October Alfalfa 采购总和。
                    # 根据通常此类 Task 设计，数值应为精确匹配。
                    if val == 2000: # 这里的 2000 是预设逻辑值
                        sub_score = 50
                    elif 1900 <= val <= 2100: # 允许少量计算误差
                        sub_score = 30
                    else:
                        sub_score = 0
                else:
                    sub_score = 0
            
            score_details.append({
                "item": "Alfalfa 采购总量计算 (Oct 2023)",
                "score": sub_score,
                "max_score": 50,
                "passed": sub_score == 50,
                "reason": f"提取数值为 {val if numbers else 'None'}，预期 2000"
            })
            total_score += sub_score
        except Exception as e:
             score_details.append({"item": "Alfalfa 采购总量计算", "score": 0, "max_score": 50, "passed": False, "reason": str(e)})

    # 最终分汇总
    total_score = min(100, max(0, total_score))
    output = {"total_score": int(total_score), "details": score_details}
    
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
