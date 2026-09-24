import os
import sys
import json
import httpx
from openai import OpenAI
import re

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
    results = []
    total_score = 0
    
    target_file = os.path.join(workspace, "debug", "root_cause.json")
    
    # 1. 检查文件是否存在
    file_exists = os.path.exists(target_file)
    if file_exists:
        results.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 debug/root_cause.json 存在"})
        total_score += 10
    else:
        results.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 debug/root_cause.json 不存在"})
        
    # 如果文件不存在，立即填充0分详情并返回
    if not file_exists:
        results.extend([
            {"item": "JSON格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"},
            {"item": "验证键名完整性(无多余或缺失)", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"},
            {"item": "验证值的字符串格式", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"},
            {"item": "设备地址(device_addr)校验", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"},
            {"item": "寄存器地址(reg_addr)校验", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"},
            {"item": "致溃脏值(bad_value)校验", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"}
        ])
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)
        return

    # 2. 检查 JSON 解析
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("JSON Root is not a dict structure")
        results.append({"item": "JSON格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的JSON对象"})
        total_score += 10
    except Exception as e:
        results.append({"item": "JSON格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"无法解析或非字典格式: {e}"})
        results.extend([
            {"item": "验证键名完整性(无多余或缺失)", "score": 0, "max_score": 10, "passed": False, "reason": "JSON不合法"},
            {"item": "验证值的字符串格式", "score": 0, "max_score": 10, "passed": False, "reason": "JSON不合法"},
            {"item": "设备地址(device_addr)校验", "score": 0, "max_score": 20, "passed": False, "reason": "JSON不合法"},
            {"item": "寄存器地址(reg_addr)校验", "score": 0, "max_score": 20, "passed": False, "reason": "JSON不合法"},
            {"item": "致溃脏值(bad_value)校验", "score": 0, "max_score": 20, "passed": False, "reason": "JSON不合法"}
        ])
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)
        return

    # 3. 验证键名完整与无多余字段 (一票否决多余字段)
    expected_keys = {"device_addr", "reg_addr", "bad_value"}
    actual_keys = set(data.keys())
    if actual_keys == expected_keys:
        results.append({"item": "验证键名完整性(无多余或缺失)", "score": 10, "max_score": 10, "passed": True, "reason": "精准包含要求的三项关键数据且无冗余字段捏造"})
        total_score += 10
    else:
        results.append({"item": "验证键名完整性(无多余或缺失)", "score": 0, "max_score": 10, "passed": False, "reason": f"键名不合规，幻觉或多写了废话字段。预期: {expected_keys}，实际: {actual_keys}"})

    # 4. 验证值的格式 (强制为大写 0xXX)
    format_passed = True
    for key in expected_keys:
        if key in data:
            val = str(data[key])
            if not re.match(r"^0x[0-9A-F]{2}$", val):
                format_passed = False
                break
        else:
            format_passed = False
            
    if format_passed:
        results.append({"item": "验证值的字符串格式", "score": 10, "max_score": 10, "passed": True, "reason": "所有字段值均严格遵循大写十六进制字符串格式规范"})
        total_score += 10
    else:
        results.append({"item": "验证值的字符串格式", "score": 0, "max_score": 10, "passed": False, "reason": "格式错误，未遵守 0xXX(纯大写) 格式规范或类型不为纯字符串"})

    # 辅助函数：严格提取HEX数字
    def parse_hex(val):
        try:
            return int(str(val), 16)
        except:
            return -1

    # 5. 校验具体的数值逻辑计算提取能力
    # device_addr (20 分)
    dev_addr_val = data.get("device_addr", "")
    dev_num = parse_hex(dev_addr_val)
    if dev_num == 0x5C:
        results.append({"item": "设备地址(device_addr)校验", "score": 20, "max_score": 20, "passed": True, "reason": "精准识别出 PMIC 的 7位I2C 地址 (0x5C)"})
        total_score += 20
    elif dev_num == 0xB8:
        results.append({"item": "设备地址(device_addr)校验", "score": 10, "max_score": 20, "passed": False, "reason": "寻址逻辑一半正确：找到了总线传输字节 0xB8，但未能正确右移还原为 7位地址 0x5C"})
        total_score += 10
    else:
        results.append({"item": "设备地址(device_addr)校验", "score": 0, "max_score": 20, "passed": False, "reason": f"设备地址错误或未找到，实际填写: {dev_addr_val}"})

    # reg_addr (20 分)
    reg_addr_val = data.get("reg_addr", "")
    reg_num = parse_hex(reg_addr_val)
    if reg_num == 0x3A:
        results.append({"item": "寄存器地址(reg_addr)校验", "score": 20, "max_score": 20, "passed": True, "reason": "LDO_CFG 寄存器地址提取正确 (0x3A)"})
        total_score += 20
    else:
        results.append({"item": "寄存器地址(reg_addr)校验", "score": 0, "max_score": 20, "passed": False, "reason": f"寄存器地址提取错误，实际填写: {reg_addr_val}"})

    # bad_value (20 分)
    bad_val_str = data.get("bad_value", "")
    bad_num = parse_hex(bad_val_str)
    if bad_num == 0x4F:
        results.append({"item": "致溃脏值(bad_value)校验", "score": 20, "max_score": 20, "passed": True, "reason": "成功找出了触发掩码位(Bit 3&6)同时拉高的致命写入数值 (0x4F)"})
        total_score += 20
    else:
        results.append({"item": "致溃脏值(bad_value)校验", "score": 0, "max_score": 20, "passed": False, "reason": f"致命触发数值错误，实际填写: {bad_val_str}"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
