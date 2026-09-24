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

def verify_workplace(workspace):
    score = 0
    details = []
    
    intel_dir = os.path.join(workspace, "intel")
    iocs_file = os.path.join(intel_dir, "iocs.json")
    
    # 1. 检查目录与文件是否存在 (10 分)
    if os.path.isdir(intel_dir) and os.path.isfile(iocs_file):
        details.append({"item": "检查结果目录与目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 intel/iocs.json 存在"})
        score += 10
    else:
        details.append({"item": "检查结果目录与目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 intel/iocs.json 文件或目录"})
        write_score(score, details, workspace)
        return

    # 2. 检查 JSON 格式合法性及结构严谨度 (10 分)
    try:
        with open(iocs_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            # 严格防止 Agent 幻觉或将大量数据直接全部导出作为 value 的作弊行为
            if len(data.keys()) > 3:
                details.append({"item": "检查 JSON 格式及结构严谨度", "score": 0, "max_score": 10, "passed": False, "reason": f"结构合法，但包含 {len(data.keys())} 个键，存在幻觉或冗余输出的作弊嫌疑"})
            else:
                details.append({"item": "检查 JSON 格式及结构严谨度", "score": 10, "max_score": 10, "passed": True, "reason": "合法的 JSON 字典结构，且无严重数据冗余"})
                score += 10
        else:
            details.append({"item": "检查 JSON 格式及结构严谨度", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 格式有效，但根节点不是预期的字典类型"})
            write_score(score, details, workspace)
            return
    except Exception as e:
        details.append({"item": "检查 JSON 格式及结构严谨度", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        write_score(score, details, workspace)
        return

    # 3 & 4. 精准比对确定性的业务结果 (各 30 分)
    expected_path = r"c:/users/public/videos/svchost_stage2.exe"
    expected_hex = "4D5A90000300000004000000FFFF0000"
    
    path_found = False
    hex_found = False
    
    for v in data.values():
        if not isinstance(v, str):
            continue
            
        # 归一化：处理路径分隔符差异和大小写
        v_path = v.replace("\\", "/").lower().strip()
        # 归一化：剥除所有空格以适应不同的 hex 展现形式
        v_hex = v.replace(" ", "").upper().strip()
        
        # 长度限制防止暴力照搬原文（超过200/100字符不认为是精准提取）
        if len(v_path) < 200 and expected_path in v_path:
            path_found = True
        if len(v_hex) < 100 and expected_hex in v_hex:
            hex_found = True

    if path_found:
        details.append({"item": "精准验证开机自启恶意路径提取", "score": 30, "max_score": 30, "passed": True, "reason": "正确提取了隐藏在茫茫系统调用日志中的目标文件路径"})
        score += 30
    else:
        details.append({"item": "精准验证开机自启恶意路径提取", "score": 0, "max_score": 30, "passed": False, "reason": "未能精准提取并转换对应的启动项文件路径"})
        
    if hex_found:
        details.append({"item": "精准验证 16 字节内存脱壳特征码", "score": 30, "max_score": 30, "passed": True, "reason": "正确提取了指定偏移量位置的纯净 16 字节特征码"})
        score += 30
    else:
        details.append({"item": "精准验证 16 字节内存脱壳特征码", "score": 0, "max_score": 30, "passed": False, "reason": "未找到预期的特征码，或未进行 ASCII 数据清理清洗"})

    # 5. 利用大模型对非结构化、由 Agent 自定义的键名进行语义检验 (20 分)
    keys_str = ", ".join(data.keys())
    llm_prompt = (
        "The file content below represents the JSON keys an agent created to store Indicators of Compromise (IOCs).\n"
        "According to the instruction, one key must logically represent an 'autostart file path' or 'registry payload',\n"
        "and the other must represent a 'hex signature', 'MZ header', or 'file magic bytes'.\n"
        "Are these keys appropriately named and easy for a human security analyst to read and understand?\n"
    )
    
    if llm_judge_content(llm_prompt, f"JSON Keys Submitted: [{keys_str}]"):
        details.append({"item": "LLM 语义校验：自定义键名可读性及专业度", "score": 20, "max_score": 20, "passed": True, "reason": f"大模型裁判认为自定义键名 [{keys_str}] 符合业务逻辑且人类可读"})
        score += 20
    else:
        details.append({"item": "LLM 语义校验：自定义键名可读性及专业度", "score": 0, "max_score": 20, "passed": False, "reason": f"大模型裁判认为键名 [{keys_str}] 缺乏合理性、不知所云或未能概括数据属性"})

    write_score(score, details, workspace)

def write_score(score, details, workspace):
    output = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    print(f"Verification completed. Score: {score}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
