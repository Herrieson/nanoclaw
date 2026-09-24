import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------------------------------------------------------
# 🔒 核心配置与 API 规范
# ----------------------------------------------------------------
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

# ----------------------------------------------------------------
# 🔒 验证逻辑设计
# ----------------------------------------------------------------
def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results_dir = os.path.join(workspace, "results")
    callback_file = os.path.join(results_dir, "callback_list.json")
    supplies_file = os.path.join(results_dir, "supplies_needed.txt")
    
    score_details = []
    
    # 1. 目录与文件存在性检查 (10分)
    if os.path.exists(results_dir) and os.path.isdir(results_dir):
        score_details.append({"item": "检查 results 目录", "score": 5, "max_score": 5, "passed": True, "reason": "目录已创建"})
    else:
        score_details.append({"item": "检查 results 目录", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 results 目录"})

    # 2. 耗材统计验证 (20分)
    # 计算逻辑：去重后的 Patient ID 分别是 101-110。
    # kits_used 原始分布：
    # 101: 1, 102: 1, 103: 1, 104: 2, 105: 1, 106: 1, 107: 1, 108: 1, 109: 2, 110: 1
    # 总计：1+1+1+2+1+1+1+1+2+1 = 12
    # 注意：105 在 booth2 记为 0，102 在 booth2 记为 1。题目说“去重后计一次，不介意保留哪个”。
    # 只要在 11 (Marvin 计 0) 到 12 (Marvin 计 1) 之间均可视为理解正确。
    expected_kits_range = [11, 12]
    if os.path.exists(supplies_file):
        try:
            with open(supplies_file, 'r') as f:
                content = f.read().strip()
                # 提取数字
                import re
                match = re.search(r'\d+', content)
                if match and int(match.group()) in expected_kits_range:
                    score_details.append({"item": "耗材数量统计", "score": 20, "max_score": 20, "passed": True, "reason": f"统计结果 {match.group()} 正确"})
                else:
                    val = match.group() if match else "None"
                    score_details.append({"item": "耗材数量统计", "score": 0, "max_score": 20, "passed": False, "reason": f"统计结果错误，预期 11 或 12，实际得到 {val}"})
        except Exception as e:
            score_details.append({"item": "耗材数量统计", "score": 0, "max_score": 20, "passed": False, "reason": f"读取或解析文件失败: {e}"})
    else:
        score_details.append({"item": "耗材数量统计", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 supplies_needed.txt"})

    # 3. 回访名单 JSON 格式与逻辑验证 (50分)
    # 筛选标准：SBP >= 140 OR DBP >= 90 OR Consent == No
    # 101: 110/70, Y -> No
    # 102: 142/80, Y -> YES (SBP)
    # 103: 120/92, Y -> YES (DBP)
    # 104: 115/75, N -> YES (Consent)
    # 105: 118/78, Y -> No
    # 106: 125/80, Y -> No
    # 107: 139/89, Y -> No
    # 108: 150/95, N -> YES (All)
    # 109: 110/70, Y -> No
    # 110: 100/60, Y -> No
    # 必选 ID：102, 103, 104, 108 (需全对)
    expected_callback_ids = {"102", "103", "104", "108"}
    if os.path.exists(callback_file):
        try:
            with open(callback_file, 'r') as f:
                data = json.load(f)
                # 转换所有 ID 为字符串进行比较
                actual_ids = set(str(i) for i in data)
                if actual_ids == expected_callback_ids:
                    score_details.append({"item": "回访名单逻辑筛选", "score": 50, "max_score": 50, "passed": True, "reason": "名单完全正确"})
                else:
                    missing = expected_callback_ids - actual_ids
                    extra = actual_ids - expected_callback_ids
                    score_details.append({"item": "回访名单逻辑筛选", "score": 20, "max_score": 50, "passed": False, "reason": f"名单不匹配。缺失: {missing}, 多余: {extra}"})
        except Exception as e:
            score_details.append({"item": "回访名单逻辑筛选", "score": 0, "max_score": 50, "passed": False, "reason": f"JSON解析失败: {e}"})
    else:
        score_details.append({"item": "回访名单逻辑筛选", "score": 0, "max_score": 50, "passed": False, "reason": "未找到 callback_list.json"})

    # 4. 去重与工具调用合理性 (20分)
    # 通过 LLM 检查 Agent 是否在最终报告或思考过程中体现了对去重的处理
    # 虽然 trace 会查调用次数，但结果域也要看最终文件是否混入了重复 ID
    if os.path.exists(callback_file):
        with open(callback_file, 'r') as f:
            data = json.load(f)
            if len(data) == len(set(data)):
                score_details.append({"item": "结果去重检查", "score": 20, "max_score": 20, "passed": True, "reason": "callback_list.json 中无重复 ID"})
            else:
                score_details.append({"item": "结果去重检查", "score": 0, "max_score": 20, "passed": False, "reason": "结果中存在重复 ID"})
    else:
        score_details.append({"item": "结果去重检查", "score": 0, "max_score": 20, "passed": False, "reason": "结果文件缺失"})

    # ----------------------------------------------------------------
    # 🔒 计算总分并输出
    # ----------------------------------------------------------------
    total_score = sum(d["score"] for d in score_details)
    output_data = {
        "total_score": int(total_score),
        "details": score_details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_verification()
