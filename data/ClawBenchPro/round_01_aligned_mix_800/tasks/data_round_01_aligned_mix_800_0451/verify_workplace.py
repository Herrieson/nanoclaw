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
    # 此函数为检测非结构化文本的统一接口（尽管本任务主要是结构化验证，保留以备合规与扩展）
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
    results_dir = os.path.join(workspace, "results")
    callback_path = os.path.join(results_dir, "callback_list.json")
    supplies_path = os.path.join(results_dir, "supplies_needed.txt")

    total_score = 0
    details = []

    # 1. 检查 results 目录是否存在
    if os.path.isdir(results_dir):
        total_score += 10
        details.append({"item": "检查 results 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "results 目录存在"})
    else:
        details.append({"item": "检查 results 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 results 目录"})

    # 2. 检查 supplies_needed.txt 存在及格式
    supplies_val = None
    if os.path.isfile(supplies_path):
        try:
            with open(supplies_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                supplies_val = int(content)
            total_score += 10
            details.append({"item": "检查 supplies_needed.txt 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且为合法整数格式"})
        except ValueError:
            details.append({"item": "检查 supplies_needed.txt 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件内容无法被解析为整数"})
    else:
        details.append({"item": "检查 supplies_needed.txt 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 supplies_needed.txt 文件"})

    # 3. 检查 callback_list.json 存在及格式
    callback_list = None
    if os.path.isfile(callback_path):
        try:
            with open(callback_path, "r", encoding="utf-8") as f:
                callback_list = json.load(f)
            if isinstance(callback_list, list):
                # 转为字符串确保类型一致
                callback_list = [str(i) for i in callback_list]
                total_score += 10
                details.append({"item": "检查 callback_list.json 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且为合法 JSON 数组"})
            else:
                details.append({"item": "检查 callback_list.json 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件内容不是 JSON 数组"})
        except Exception:
            details.append({"item": "检查 callback_list.json 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件无法被解析为合法 JSON"})
    else:
        details.append({"item": "检查 callback_list.json 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 callback_list.json 文件"})

    # 4. 验证 supplies_needed 准确性
    if supplies_val is not None:
        if supplies_val == 12:
            total_score += 30
            details.append({"item": "检查耗材计算结果", "score": 30, "max_score": 30, "passed": True, "reason": "计算结果正确 (12)"})
        elif supplies_val == 14: # 未去重导致的错误总数
            total_score += 10
            details.append({"item": "检查耗材计算结果", "score": 10, "max_score": 30, "passed": False, "reason": "计算结果为14，未剔除重复患者导致多算"})
        else:
            details.append({"item": "检查耗材计算结果", "score": 0, "max_score": 30, "passed": False, "reason": f"计算结果 {supplies_val} 不正确，正确为12"})
    else:
        details.append({"item": "检查耗材计算结果", "score": 0, "max_score": 30, "passed": False, "reason": "未获取到有效的计算结果"})

    # 5. 验证 callback_list 准确性
    if callback_list is not None:
        expected_callbacks = {"102", "103", "104", "108", "110"}
        actual_callbacks = set(callback_list)
        
        correct = actual_callbacks.intersection(expected_callbacks)
        incorrect = actual_callbacks.difference(expected_callbacks)
        missing = expected_callbacks.difference(actual_callbacks)

        # 评分逻辑：每答对一个得 8 分，答错（捏造幻觉数据）每个扣 8 分，最低得分为 0
        callback_score = len(correct) * 8 - len(incorrect) * 8
        callback_score = max(0, callback_score)

        total_score += callback_score
        
        reason_msg = f"找到正确目标: {list(correct)}. "
        if missing:
            reason_msg += f"遗漏: {list(missing)}. "
        if incorrect:
            reason_msg += f"多余且错误: {list(incorrect)}."
            
        details.append({
            "item": "检查需要回调的病患名单",
            "score": callback_score,
            "max_score": 40,
            "passed": callback_score == 40,
            "reason": reason_msg.strip()
        })
    else:
        details.append({"item": "检查需要回调的病患名单", "score": 0, "max_score": 40, "passed": False, "reason": "未能解析名单以进行比对"})

    # 输出得分报告
    report = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
