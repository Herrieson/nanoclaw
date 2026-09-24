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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "report", "failed_init.json")
    
    total_score = 0
    details = []

    # 1. 检查目标文件是否存在 (20分)
    if os.path.isfile(target_file):
        total_score += 20
        details.append({"item": "检查结果文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件 report/failed_init.json 存在"})
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件 report/failed_init.json 不存在"})
        write_score(total_score, details)
        return

    # 2. 检查文件是否为合法的 JSON 格式 (20分)
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        total_score += 20
        details.append({"item": "检查文件是否为合法 JSON", "score": 20, "max_score": 20, "passed": True, "reason": "成功解析 JSON 文件"})
    except json.JSONDecodeError:
        details.append({"item": "检查文件是否为合法 JSON", "score": 0, "max_score": 20, "passed": False, "reason": "文件内容不是合法的 JSON 格式"})
        write_score(total_score, details)
        return
    except Exception as e:
        details.append({"item": "检查文件是否为合法 JSON", "score": 0, "max_score": 20, "passed": False, "reason": f"文件读取发生未知错误: {str(e)}"})
        write_score(total_score, details)
        return

    # 3. 检查 JSON 字段完整性 (10分)
    if not isinstance(data, dict):
        details.append({"item": "检查 JSON 结构类型", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 根节点必须是一个对象 (dict)"})
        write_score(total_score, details)
        return

    has_register = "register" in data
    has_value = "value" in data
    extra_keys = set(data.keys()) - {"register", "value"}

    if has_register and has_value:
        if extra_keys:
            # 存在冗余字段，扣5分
            total_score += 5
            details.append({"item": "检查 JSON 字段", "score": 5, "max_score": 10, "passed": False, "reason": f"包含了必要的字段，但存在冗余字段: {extra_keys}"})
        else:
            total_score += 10
            details.append({"item": "检查 JSON 字段", "score": 10, "max_score": 10, "passed": True, "reason": "精确包含了 register 和 value 字段"})
    else:
        details.append({"item": "检查 JSON 字段", "score": 0, "max_score": 10, "passed": False, "reason": "缺失 register 或 value 字段"})
        write_score(total_score, details)
        return

    # 4. 提取并校验 register 的值 (25分)
    reg_val = str(data.get("register", "")).strip().lower()
    if reg_val == "0x2a":
        total_score += 25
        details.append({"item": "校验报错的寄存器地址", "score": 25, "max_score": 25, "passed": True, "reason": "找到了正确的寄存器地址 0x2A"})
    else:
        details.append({"item": "校验报错的寄存器地址", "score": 0, "max_score": 25, "passed": False, "reason": f"寄存器地址错误或格式不标准，预期 '0x2A'，实际获取到 '{reg_val}'"})

    # 5. 提取并校验 value 的值 (25分)
    val_val = str(data.get("value", "")).strip().lower()
    if val_val == "0x7f":
        total_score += 25
        details.append({"item": "校验试图写入的错误数据", "score": 25, "max_score": 25, "passed": True, "reason": "找到了正确的报错数据 0x7F"})
    else:
        details.append({"item": "校验试图写入的错误数据", "score": 0, "max_score": 25, "passed": False, "reason": f"试图写入的数据错误或格式不标准，预期 '0x7F'，实际获取到 '{val_val}'"})

    write_score(total_score, details)

def write_score(total_score, details):
    report = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    verify()
