import os
import sys
import json
import httpx
from openai import OpenAI

# 环境变量配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """检测非结构化文本的统一接口"""
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

def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables", "clean_results.json")
    
    score = 0
    details = []

    # 1. 检查交付文件是否存在 (10分)
    if os.path.exists(deliverables_path):
        score += 10
        details.append({"item": "交付文件存在性检查", "score": 10, "max_score": 10, "passed": True, "reason": "clean_results.json 已生成"})
        
        try:
            with open(deliverables_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 2. 检查 JSON 结构合法性 (10分)
            required_keys = ["good_samples_count", "average_rfu", "filtered_data"]
            if all(k in data for k in required_keys):
                score += 10
                details.append({"item": "JSON结构合法性", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有必要字段"})
            else:
                details.append({"item": "JSON结构合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失字段: {[k for k in required_keys if k not in data]}"})

            # 3. 核心计算逻辑验证 - 过滤阈值 0-800 (50分)
            # 有效数据点: Batch A (150.5, 250.0), Batch B (300.5, 500.0) -> 共4个
            # 排除点: Batch A (-40.2), Batch B (950.0, 801.0)
            expected_count = 4
            expected_avg = (150.5 + 250.0 + 300.5 + 500.0) / 4 # 300.25
            
            count_passed = data.get("good_samples_count") == expected_count
            avg_passed = abs(data.get("average_rfu", 0) - expected_avg) < 0.01
            
            if count_passed and avg_passed:
                score += 50
                details.append({"item": "数据过滤与均值计算", "score": 50, "max_score": 50, "passed": True, "reason": "样本计数(4)与均值(300.25)完全正确"})
            elif count_passed:
                score += 25
                details.append({"item": "数据过滤与均值计算", "score": 25, "max_score": 50, "passed": False, "reason": f"计数正确但均值错误，期望 {expected_avg}"})
            else:
                details.append({"item": "数据过滤与均值计算", "score": 0, "max_score": 50, "passed": False, "reason": "计数与均值均不符合 0-800 过滤标准"})

            # 4. 检查是否包含多余或虚构数据 (10分)
            # 检查 filtered_data 列表是否只包含正确的样本 ID
            expected_ids = {"S001", "S002", "S005", "S006"}
            actual_ids = {item["sample_id"] for item in data.get("filtered_data", []) if "sample_id" in item}
            if actual_ids == expected_ids:
                score += 10
                details.append({"item": "样本明细准确性", "score": 10, "max_score": 10, "passed": True, "reason": "明细数据与原始有效数据严格一致"})
            else:
                details.append({"item": "样本明细准确性", "score": 0, "max_score": 10, "passed": False, "reason": "明细数据中存在多余或缺失的样本ID"})

            # 5. 利用 LLM 检查实验报告概括（如果存在总结字段） (20分)
            # 假设 Agent 可能在 JSON 中添加了 summary 字段或通过日志输出了结论
            summary_text = str(data)
            prompt = "The data is for 'In Vivo Metabolic Study v4'. Does the content correctly imply the filtering threshold was 0-800 based on lab protocols?"
            if llm_judge_content(prompt, summary_text):
                score += 20
                details.append({"item": "业务上下文理解(LLM)", "score": 20, "max_score": 20, "passed": True, "reason": "结果体现了对 v4 协议阈值的正确应用"})
            else:
                details.append({"item": "业务上下文理解(LLM)", "score": 0, "max_score": 20, "passed": False, "reason": "结果未能体现是从知识库获取的 0-800 阈值"})

        except Exception as e:
            details.append({"item": "文件解析异常", "score": 0, "max_score": 90, "passed": False, "reason": str(e)})
    else:
        details.append({"item": "交付文件存在性检查", "score": 0, "max_score": 100, "passed": False, "reason": "deliverables/clean_results.json 未找到"})

    # 写入最终评分
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_verification()
