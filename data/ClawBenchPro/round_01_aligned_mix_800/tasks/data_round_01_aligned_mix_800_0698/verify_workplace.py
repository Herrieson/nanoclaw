import os
import sys
import json
import httpx
from openai import OpenAI

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
    # 此函数为检测非结构化文本的统一接口
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []

    target_dir = os.path.join(workspace, "financial_forecast")
    target_file = os.path.join(target_dir, "dinner_budget.json")

    # 1. 检查文件是否存在 (10 分)
    if os.path.exists(target_file):
        details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "dinner_budget.json 存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 dinner_budget.json"})
        
    # 2. 检查 JSON 格式合法性及解析 (15 分)
    data = None
    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            details.append({"item": "检查 JSON 格式合法性", "score": 15, "max_score": 15, "passed": True, "reason": "文件是合法的 JSON 格式"})
            total_score += 15
        except Exception as e:
            details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON 解析失败: {e}"})

    # 3. LLM 检查 Keys 的命名语义是否清晰 (15 分)
    if data and isinstance(data, dict):
        keys_str = ", ".join(data.keys())
        prompt = "Does the following list of JSON keys clearly and unambiguously represent both 'the absolute total final cost in USD' and 'the list of flagged items for inflation'? Answer YES if both concepts are clearly represented by the keys, otherwise NO."
        if llm_judge_content(prompt, keys_str):
            details.append({"item": "利用大模型检查 Keys 命名语义", "score": 15, "max_score": 15, "passed": True, "reason": "大模型判定 Keys 的命名清晰地反映了总价与异常清单"})
            total_score += 15
        else:
            details.append({"item": "利用大模型检查 Keys 命名语义", "score": 0, "max_score": 15, "passed": False, "reason": f"大模型认为 Keys 命名不够清晰或缺少必要含义。Keys: {keys_str}"})
    else:
        details.append({"item": "利用大模型检查 Keys 命名语义", "score": 0, "max_score": 15, "passed": False, "reason": "无法解析字典以获取 keys"})

    # 4. 检查总价是否准确计算 (30 分)
    # 正确结果应该是 446.4
    if data and isinstance(data, dict):
        found_cost = False
        for k, v in data.items():
            if isinstance(v, (int, float)):
                if abs(v - 446.4) < 0.01:
                    found_cost = True
                    break
        
        if found_cost:
            details.append({"item": "检查总价计算结果", "score": 30, "max_score": 30, "passed": True, "reason": "精确找到了 446.4 的总价计算结果"})
            total_score += 30
        else:
            details.append({"item": "检查总价计算结果", "score": 0, "max_score": 30, "passed": False, "reason": "JSON 中未找到计算准确的 446.4 总价值"})
    else:
        details.append({"item": "检查总价计算结果", "score": 0, "max_score": 30, "passed": False, "reason": "数据不合法"})

    # 5. 检查 Flagged Items 的准确性 (30 分)
    # 正确结果只应包含 "Lobster", "Chardonnay"
    if data and isinstance(data, dict):
        found_list = False
        target_set = {"lobster", "chardonnay"}
        for k, v in data.items():
            if isinstance(v, list):
                # 转为小写比较
                str_list = [str(x).lower() for x in v]
                current_set = set(str_list)
                if current_set == target_set and len(str_list) == len(target_set):
                    found_list = True
                    break
        
        if found_list:
            details.append({"item": "检查异常清单提取是否正确", "score": 30, "max_score": 30, "passed": True, "reason": "准确识别并仅包含了 Lobster 和 Chardonnay"})
            total_score += 30
        else:
            details.append({"item": "检查异常清单提取是否正确", "score": 0, "max_score": 30, "passed": False, "reason": "未找到匹配正确的 Flagged Items 列表，可能存在遗漏或幻觉捏造"})
    else:
        details.append({"item": "检查异常清单提取是否正确", "score": 0, "max_score": 30, "passed": False, "reason": "数据不合法"})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.append = json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
