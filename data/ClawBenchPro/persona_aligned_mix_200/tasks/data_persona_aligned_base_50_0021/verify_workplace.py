import os
import sys
import json
import httpx
import re
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """用于对非结构化文本内容进行兜底或辅助语义判定"""
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
    # 动态获取沙盒挂载的工作区路径
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_json_path = os.path.join(workspace, "debug", "root_cause.json")
    
    total_score = 0
    details = []

    # 1. 检查物理文件是否存在 (10 分)
    if not os.path.exists(target_json_path):
        details.append({
            "item": "检查目标文件是否存在", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": "未找到 debug/root_cause.json 文件，Agent 未能在指定路径输出结果"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2, ensure_ascii=False)
        return
    else:
        details.append({
            "item": "检查目标文件是否存在", 
            "score": 10, 
            "max_score": 10, 
            "passed": True, 
            "reason": "文件 debug/root_cause.json 存在"
        })
        total_score += 10

    # 2. 检查 JSON 语法合法性 (10 分)
    try:
        with open(target_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式解析", 
            "score": 10, 
            "max_score": 10, 
            "passed": True, 
            "reason": "JSON 格式合法且可被标准库解析"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON 格式解析", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": f"解析失败，可能混入了多余字符或 markdown 格式: {e}"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 3. 检查 JSON Schema 完整性与数据类型 (20 分)
    # 不允许少任何一个键，也不允许多出胡编乱造的键
    expected_keys = {"device_addr", "reg_addr", "bad_value"}
    actual_keys = set(data.keys()) if isinstance(data, dict) else set()
    
    if actual_keys == expected_keys:
        if all(isinstance(data[k], str) for k in expected_keys):
            # 严格检查值是否为 "0x" 加上两个十六进制字符（大小写均可）
            format_pass = all(re.match(r"^0x[0-9a-fA-F]{2}$", data[k]) for k in expected_keys)
            if format_pass:
                details.append({
                    "item": "Schema 完整性与类型验证", 
                    "score": 20, 
                    "max_score": 20, 
                    "passed": True, 
                    "reason": "所有必填键均存在，无幻觉字段，且值严格遵循标准的 0xXX 字符串格式"
                })
                total_score += 20
            else:
                details.append({
                    "item": "Schema 完整性与类型验证", 
                    "score": 10, 
                    "max_score": 20, 
                    "passed": False, 
                    "reason": "键正确且为字符串，但值未严格遵循 0xXX 的标准两位十六进制格式"
                })
                total_score += 10
        else:
            details.append({
                "item": "Schema 完整性与类型验证", 
                "score": 5, 
                "max_score": 20, 
                "passed": False, 
                "reason": "键正确，但部分数据不是纯字符串类型（如被写为整数或包含其它嵌套结构）"
            })
            total_score += 5
    else:
        missing = expected_keys - actual_keys
        extra = actual_keys - expected_keys
        reason_parts = []
        if missing: reason_parts.append(f"缺少必填键: {missing}")
        if extra: reason_parts.append(f"捏造或多余键: {extra}")
        details.append({
            "item": "Schema 完整性与类型验证", 
            "score": 0, 
            "max_score": 20, 
            "passed": False, 
            "reason": " | ".join(reason_parts)
        })

    # 4. 严格值校验: device_addr (20 分)
    device_addr = str(data.get("device_addr", "")).strip().lower()
    if device_addr == "0x68":
        details.append({
            "item": "校验设备地址(device_addr)", 
            "score": 20, 
            "max_score": 20, 
            "passed": True, 
            "reason": "准确提取 I2C 基地址 0x68"
        })
        total_score += 20
    elif device_addr == "0xd0":
        details.append({
            "item": "校验设备地址(device_addr)", 
            "score": 10, 
            "max_score": 20, 
            "passed": False, 
            "reason": "提取到 0xD0 (这是带 Write 位偏移后的传输地址)，虽然对应了抓包字节，但规范的 Base Addr 应为 0x68"
        })
        total_score += 10
    else:
        details.append({
            "item": "校验设备地址(device_addr)", 
            "score": 0, 
            "max_score": 20, 
            "passed": False, 
            "reason": f"提取错误: {device_addr}"
        })

    # 5. 严格值校验: reg_addr (20 分)
    reg_addr = str(data.get("reg_addr", "")).strip().lower()
    if reg_addr == "0x6b":
        details.append({
            "item": "校验寄存器地址(reg_addr)", 
            "score": 20, 
            "max_score": 20, 
            "passed": True, 
            "reason": "准确提取触发死锁的 PWR_MGMT_1 寄存器地址 0x6B"
        })
        total_score += 20
    else:
        details.append({
            "item": "校验寄存器地址(reg_addr)", 
            "score": 0, 
            "max_score": 20, 
            "passed": False, 
            "reason": f"寄存器地址提取错误: {reg_addr}"
        })

    # 6. 严格值校验: bad_value (20 分)
    bad_value = str(data.get("bad_value", "")).strip().lower()
    if bad_value == "0x80":
        details.append({
            "item": "校验致死错值(bad_value)", 
            "score": 20, 
            "max_score": 20, 
            "passed": True, 
            "reason": "准确提取触发 Errata 并导致看门狗复位的脏值 0x80"
        })
        total_score += 20
    else:
        details.append({
            "item": "校验致死错值(bad_value)", 
            "score": 0, 
            "max_score": 20, 
            "passed": False, 
            "reason": f"错误值提取错误: {bad_value}"
        })

    # 写入最终判卷结果
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
