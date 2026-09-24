import os
import sys
import json
import httpx
from openai import OpenAI

# 配置环境常量
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    prep_dir = os.path.join(workspace, "delivery_prep")
    problem_file = os.path.join(prep_dir, "problem_packages.txt")
    summary_file = os.path.join(prep_dir, "route_summary.json")
    
    score_details = []
    total_score = 0

    # 1. 基础目录与文件存在性检查 (10分)
    dir_exists = os.path.exists(prep_dir)
    prob_exists = os.path.exists(problem_file)
    sum_exists = os.path.exists(summary_file)
    
    score_1 = (5 if dir_exists else 0) + (2.5 if prob_exists else 0) + (2.5 if sum_exists else 0)
    score_details.append({"item": "目录与文件结构检查", "score": score_1, "max_score": 10, "passed": score_1 == 10, "reason": "检查 delivery_prep 目录及相关文件是否存在"})
    total_score += score_1

    # 2. 问题包裹列表准确性 (40分)
    # 预期问题包裹:
    # PKG-1002 (Weight 0x3F=63.0 > 50)
    # PKG-1003 (Zip length 4 != 5)
    # PKG-2002 (Weight 60.5 > 50)
    # PKG-2003 (Zip 99999 is Discontinued)
    # PKG-3002 (Weight 0x33=51.0 > 50)
    expected_problems = {"PKG-1002", "PKG-1003", "PKG-2002", "PKG-2003", "PKG-3002"}
    
    if prob_exists:
        try:
            with open(problem_file, "r") as f:
                content = f.read().splitlines()
                actual_problems = set([line.strip() for line in content if line.strip()])
            
            # 严格匹配
            if actual_problems == expected_problems:
                prob_score = 40
                reason = "准确识别了所有超重和ZIP异常包裹"
            else:
                missing = expected_problems - actual_problems
                extra = actual_problems - expected_problems
                prob_score = max(0, 40 - (len(missing) * 10) - (len(extra) * 5))
                reason = f"识别有误。缺失: {missing}, 多余: {extra}"
        except Exception as e:
            prob_score = 0
            reason = f"解析 problem_packages.txt 失败: {e}"
    else:
        prob_score = 0
        reason = "problem_packages.txt 不存在"
    
    score_details.append({"item": "问题包裹识别准确率", "score": prob_score, "max_score": 40, "passed": prob_score == 40, "reason": reason})
    total_score += prob_score

    # 3. 统计摘要 JSON 合法性与数据准确性 (30分)
    # 预期有效包裹及其 ZIP:
    # PKG-1001: 90210
    # PKG-2001: 90210
    # PKG-3001: 33101
    # PKG-3003: 90210
    # 结果: {"90210": 3, "33101": 1}
    expected_summary = {"90210": 3, "33101": 1}
    
    if sum_exists:
        try:
            with open(summary_file, "json") as f:
                actual_summary = json.load(f)
            
            if actual_summary == expected_summary:
                sum_score = 30
                reason = "route_summary.json 数据完全准确"
            else:
                sum_score = 15 if set(actual_summary.keys()) == set(expected_summary.keys()) else 0
                reason = f"统计数据不匹配。预期: {expected_summary}, 实际: {actual_summary}"
        except Exception as e:
            sum_score = 0
            reason = f"解析 JSON 失败: {e}"
    else:
        sum_score = 0
        reason = "route_summary.json 不存在"
    
    score_details.append({"item": "统计摘要数据准确性", "score": sum_score, "max_score": 30, "passed": sum_score == 30, "reason": reason})
    total_score += sum_score

    # 4. 异常处理行为检查 - LLM 语义验证 (20分)
    # 检查 Agent 是否误收了 Discontinued 的 99999 包裹进入有效列表，或者是否对 50.0 lbs 的包裹判断错误
    # 这里通过 LLM 审阅 route_summary.json 的构成逻辑（由 Agent 产出的注释或结果决定）
    if sum_exists:
        with open(summary_file, "r") as f:
            content = f.read()
        prompt = "Check if the JSON summary correctly excludes ZIP '99999' (which is discontinued) and includes exactly 3 counts for '90210' (PKG-1001, PKG-2001, PKG-3003). Does it look correct according to rules?"
        if llm_judge_content(prompt, content):
            llm_score = 20
            reason = "LLM 验证数据过滤逻辑正确"
        else:
            llm_score = 0
            reason = "LLM 判定汇总数据中包含不应存在的包裹或统计错误"
    else:
        llm_score = 0
        reason = "无法进行 LLM 验证，文件缺失"
    
    score_details.append({"item": "LLM 逻辑合规性校验", "score": llm_score, "max_score": 20, "passed": llm_score == 20, "reason": reason})
    total_score += llm_score

    # 写入最终结果
    result = {
        "total_score": int(total_score),
        "details": score_details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
