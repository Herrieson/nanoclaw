import os
import sys
import json
import httpx
import re
import base64
from openai import OpenAI

# ----------------------------------------------------------------      
# 🔒 强制 API 规范：初始化客户端
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
# 🎯 核心逻辑：数据提取与验证项目
# ----------------------------------------------------------------

def run_evaluation():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    review_dir = os.path.join(workspace, "ready_for_review")
    score_details = []
    
    # 1. 检查目录结构 (10分)
    if os.path.exists(review_dir) and os.path.isdir(review_dir):
        score_details.append({"item": "目录 ready_for_review 存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录创建正确"})
    else:
        score_details.append({"item": "目录 ready_for_review 存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到指定结果目录"})
        # 严重错误，提前写入并退出
        finalize_score(score_details)
        return

    # 获取产物文件
    files = [f for f in os.listdir(review_dir) if os.path.isfile(os.path.join(review_dir, f))]
    if not files:
        score_details.append({"item": "结果文件产出", "score": 0, "max_score": 40, "passed": False, "reason": "目录为空"})
        finalize_score(score_details)
        return
    
    # 默认读取第一个文件
    result_file_path = os.path.join(review_dir, files[0])
    with open(result_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. 精准数值校验 (共 50 分)
    # 目标：Deductible: 1551.00, Non-Deductible: 939.99
    # 使用正则表达式提取金额并转换
    deductible_match = re.search(r"1[,]?551(\.00)?", content)
    non_deductible_match = re.search(r"939\.99", content)
    
    if deductible_match:
        score_details.append({"item": "抵扣金额计算准确 (1551.00)", "score": 25, "max_score": 25, "passed": True, "reason": "找到了正确的抵扣总额"})
    else:
        score_details.append({"item": "抵扣金额计算准确 (1551.00)", "score": 0, "max_score": 25, "passed": False, "reason": "未找到准确的抵扣总额 1551.00"})

    if non_deductible_match:
        score_details.append({"item": "非抵扣金额计算准确 (939.99)", "score": 25, "max_score": 25, "passed": True, "reason": "找到了正确的非抵扣总额"})
    else:
        score_details.append({"item": "非抵扣金额计算准确 (939.99)", "score": 0, "max_score": 25, "passed": False, "reason": "未找到准确的非抵扣总额 939.99"})

    # 3. 异常人员标记校验 (20 分)
    # 目标：EMP-042 有 3 次非抵扣记录，应被标记
    if "EMP-042" in content:
        score_details.append({"item": "异常人员标记 (EMP-042)", "score": 20, "max_score": 20, "passed": True, "reason": "成功识别并标记了违规员工 EMP-042"})
    else:
        score_details.append({"item": "异常人员标记 (EMP-042)", "score": 0, "max_score": 20, "passed": False, "reason": "未发现或未标记违规次数超限的员工 EMP-042"})

    # 4. LLM 语义与逻辑校验 (20 分)
    # 验证 Agent 是否真的理解了任务背景，而非仅仅罗列数字
    llm_prompt = "Check if the file content professionally presents a tax compliance summary, mentions the analysis of expenses, and provides clear categories. Answer YES only if it looks like a professional report for a manager."
    is_professional = llm_judge_content(llm_prompt, content)
    
    if is_professional:
        score_details.append({"item": "报告专业性与完整性 (LLM)", "score": 20, "max_score": 20, "passed": True, "reason": "报告表达专业且结构清晰"})
    else:
        score_details.append({"item": "报告专业性与完整性 (LLM)", "score": 0, "max_score": 20, "passed": False, "reason": "报告内容过于简陋或缺乏业务逻辑描述"})

    finalize_score(score_details)

def finalize_score(details):
    total = sum(item["score"] for item in details)
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_evaluation()
