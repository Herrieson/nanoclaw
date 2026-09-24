import os
import sys
import json
import re
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

def normalize_hex_string(s):
    """去除干扰字符，纯化十六进制用于宽松比对"""
    return re.sub(r'[^A-Fa-f0-9]', '', str(s)).upper()

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    json_path = os.path.join(workspace, "analysis", "dirty_tx.json")
    
    details = []
    total_score = 0

    # 1. 检查目标目录和文件是否存在 (10 分)
    if os.path.exists(json_path):
        details.append({"item": "检查目标文件 dirty_tx.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标文件 dirty_tx.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        return write_result(total_score, details)

    # 2. 解析 JSON 文件格式 (10 分)
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            details.append({"item": "检查 JSON 格式是否为字典", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功且根结构为字典"})
            total_score += 10
        else:
            details.append({"item": "检查 JSON 格式是否为字典", "score": 0, "max_score": 10, "passed": False, "reason": f"根结构不是字典，类型为 {type(data)}"})
            return write_result(total_score, details)
    except Exception as e:
        details.append({"item": "检查 JSON 格式是否为字典", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        return write_result(total_score, details)

    # 3. 检查 Transaction ID 过滤逻辑 (30 分)
    expected_keys = {"TX-1002", "TX-1008"}
    wrong_key_0c4 = "TX-1003"
    actual_keys = set(data.keys())
    
    if actual_keys == expected_keys:
        details.append({"item": "检查提取的 Transaction ID 集合", "score": 30, "max_score": 30, "passed": True, "reason": "精确提取了触发 0C7 的异常 ID，没有多余或遗漏"})
        total_score += 30
    else:
        if wrong_key_0c4 in actual_keys:
            details.append({"item": "检查提取的 Transaction ID 集合", "score": 0, "max_score": 30, "passed": False, "reason": "混入了触发 0C4 的 TX-1003 或其他非法字段，严重违反业务规则一票否决该项"})
        elif expected_keys.issubset(actual_keys):
            details.append({"item": "检查提取的 Transaction ID 集合", "score": 0, "max_score": 30, "passed": False, "reason": "包含了不应存在的捏造键，判定为幻觉或提取逻辑错误"})
        else:
            correct_cnt = len(actual_keys.intersection(expected_keys))
            score_for_keys = correct_cnt * 10
            details.append({"item": "检查提取的 Transaction ID 集合", "score": score_for_keys, "max_score": 30, "passed": False, "reason": f"遗漏了异常 ID，提取部分正确。当前键: {actual_keys}"})
            total_score += score_for_keys

    # 4. 检查 TX-1002 的 Hex 数据段提取 (25 分)
    if "TX-1002" in data:
        expected_hex_1002 = "E3E760F1F0F0F20000012A4C40404040"
        actual_raw = str(data["TX-1002"])
        actual_hex = normalize_hex_string(actual_raw)
        if actual_hex == expected_hex_1002:
            # 进一步检查是否"保留空格"
            if len(actual_raw.split()) == 16:
                details.append({"item": "校验 TX-1002 数据段准确性", "score": 25, "max_score": 25, "passed": True, "reason": "十六进制值准确无误，且保留了空格分割"})
                total_score += 25
            else:
                details.append({"item": "校验 TX-1002 数据段准确性", "score": 20, "max_score": 25, "passed": True, "reason": "十六进制数值准确，但未严格按要求保留源数据的空格结构"})
                total_score += 20
        else:
            details.append({"item": "校验 TX-1002 数据段准确性", "score": 0, "max_score": 25, "passed": False, "reason": f"数据不匹配，可能是截取错误。找到的内容: {actual_hex}"})
    else:
        details.append({"item": "校验 TX-1002 数据段准确性", "score": 0, "max_score": 25, "passed": False, "reason": "字典中缺失 TX-1002 键"})

    # 5. 检查 TX-1008 的 Hex 数据段提取 (25 分)
    if "TX-1008" in data:
        expected_hex_1008 = "E3E760F1F0F0F80000FFFFFC40404040"
        actual_raw = str(data["TX-1008"])
        actual_hex = normalize_hex_string(actual_raw)
        if actual_hex == expected_hex_1008:
            if len(actual_raw.split()) == 16:
                details.append({"item": "校验 TX-1008 数据段准确性", "score": 25, "max_score": 25, "passed": True, "reason": "十六进制值准确无误，且保留了空格分割"})
                total_score += 25
            else:
                details.append({"item": "校验 TX-1008 数据段准确性", "score": 20, "max_score": 25, "passed": True, "reason": "十六进制数值准确，但未严格按要求保留源数据的空格结构"})
                total_score += 20
        else:
            details.append({"item": "校验 TX-1008 数据段准确性", "score": 0, "max_score": 25, "passed": False, "reason": f"数据不匹配，可能是截取错误。找到的内容: {actual_hex}"})
    else:
        details.append({"item": "校验 TX-1008 数据段准确性", "score": 0, "max_score": 25, "passed": False, "reason": "字典中缺失 TX-1008 键"})

    return write_result(total_score, details)

def write_result(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return result

if __name__ == "__main__":
    verify()
