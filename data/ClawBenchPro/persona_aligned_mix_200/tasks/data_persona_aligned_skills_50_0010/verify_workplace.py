import os
import sys
import json
import httpx
from openai import OpenAI

# ==========================================
# 强制 API 规范 (LLM 初始化)
# ==========================================
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
    """
    非结构化文本的统一 LLM 检测接口
    """
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

# ==========================================
# 核心验证逻辑
# ==========================================
def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_dir = os.path.join(workspace, "report")
    target_file = os.path.join(report_dir, "failed_init.json")
    
    details = []
    total_score = 0
    
    # 1. 目录存在性验证 (10分)
    if os.path.isdir(report_dir):
        details.append({"item": "检查 report 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "report 目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查 report 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "report 目录缺失"})
        
    # 2. 目标文件存在性验证 (10分)
    if os.path.isfile(target_file):
        details.append({"item": "检查 failed_init.json 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目标 JSON 文件存在"})
        total_score += 10
    else:
        details.append({"item": "检查 failed_init.json 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目标文件缺失，可能未生成或路径错误"})
        # 严重错误，后续无法解析，直接输出
        return total_score, details

    # 3. JSON 格式及 Schema 严格校验 (30分)
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        details.append({"item": "JSON 格式合法性解析", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON 格式"})
        total_score += 10
        
        # 严查作弊与幻觉：不允许有多余字段
        expected_keys = {"register", "value"}
        actual_keys = set(data.keys())
        
        if actual_keys == expected_keys:
            details.append({"item": "严格校验 JSON 字段 (无幻觉字段)", "score": 20, "max_score": 20, "passed": True, "reason": "仅包含 register 和 value，无冗余字段"})
            total_score += 20
        else:
            details.append({"item": "严格校验 JSON 字段 (无幻觉字段)", "score": 0, "max_score": 20, "passed": False, "reason": f"包含不符合要求的字段或缺少必填字段: {list(actual_keys)}"})
            
    except json.JSONDecodeError:
        details.append({"item": "JSON 格式合法性解析", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 解析失败，格式错误"})
        details.append({"item": "严格校验 JSON 字段 (无幻觉字段)", "score": 0, "max_score": 20, "passed": False, "reason": "文件损坏无法进行字段校验"})
        return total_score, details

    # 4. 核心业务数据准确性校验 (50分)
    # Target: IMU-6800 address 0x68 -> NACK at register 0x2A with value 0x7F
    try:
        reg_val = str(data.get("register", "")).strip().lower()
        data_val = str(data.get("value", "")).strip().lower()
        
        # 校验寄存器地址 (25分)
        if reg_val == "0x2a":
            details.append({"item": "致命错误寄存器定位", "score": 25, "max_score": 25, "passed": True, "reason": "准确找出了导致瘫痪的 0x2A 寄存器"})
            total_score += 25
        elif reg_val == "0x11":
            details.append({"item": "致命错误寄存器定位", "score": 0, "max_score": 25, "passed": False, "reason": "被红鲱鱼误导，定位成了正常的 PMIC 0x11 轮询报错"})
        else:
            details.append({"item": "致命错误寄存器定位", "score": 0, "max_score": 25, "passed": False, "reason": f"寄存器地址错误: {reg_val}"})

        # 校验写入的非法数值 (25分)
        if data_val == "0x7f":
            details.append({"item": "非法写入值提取", "score": 25, "max_score": 25, "passed": True, "reason": "准确提取了当时试图写入的 0x7F 数值"})
            total_score += 25
        else:
            details.append({"item": "非法写入值提取", "score": 0, "max_score": 25, "passed": False, "reason": f"提取的写入值错误: {data_val}"})
            
    except Exception as e:
        details.append({"item": "数据精确度校验", "score": 0, "max_score": 50, "passed": False, "reason": f"数据提取发生异常: {str(e)}"})

    return total_score, details

if __name__ == "__main__":
    score, detail_list = verify()
    
    output_data = {
        "total_score": score,
        "details": detail_list
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
