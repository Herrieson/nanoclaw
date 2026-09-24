import os
import sys
import json
import httpx
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
    """大模型统一检测接口，专用于检测非结构化文本的语义合理性"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[Content to Verify]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def verify(workspace_dir):
    details = []
    total_score = 0
    
    target_file = os.path.join(workspace_dir, "iocs", "extracted_iocs.json")
    
    # 1. 检查结果文件是否存在 (10分)
    if not os.path.exists(target_file):
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 iocs/extracted_iocs.json 文件"})
        return 0, details
    
    details.append({"item": "检查目标结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目标文件存在"})
    
    # 2. 检查 JSON 格式合法性与必要字段 (20分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        required_keys = ["registry_value", "malicious_path", "unpack_signature", "ransomware_family"]
        missing_keys = [k for k in required_keys if k not in data]
        
        if missing_keys:
            details.append({"item": "检查 JSON Schema 完整性", "score": 0, "max_score": 20, "passed": False, "reason": f"缺失必要字段: {missing_keys}"})
        else:
            details.append({"item": "检查 JSON Schema 完整性", "score": 20, "max_score": 20, "passed": True, "reason": "所有要求提取的字段均已存在"})
            
    except json.JSONDecodeError:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 格式解析失败"})
        return sum(d["score"] for d in details), details

    # 3. 严格比对注册表持久化信息 (30分)
    # 基于 env_builder.py, 正确的注册表项和路径是明确的
    registry_score = 0
    reg_passed = True
    reg_reason = []
    
    if str(data.get("registry_value", "")).strip() == "WinUpdateSvc":
        registry_score += 15
    else:
        reg_passed = False
        reg_reason.append("registry_value 提取错误或含有多余字符")
        
    if str(data.get("malicious_path", "")).strip() == "C:\\Users\\Public\\winlogon.exe":
        registry_score += 15
    else:
        reg_passed = False
        reg_reason.append("malicious_path 提取错误或转义不正确")
        
    details.append({"item": "验证注册表与恶意路径信息提取的精准度", "score": registry_score, "max_score": 30, "passed": reg_passed, "reason": "、".join(reg_reason) if not reg_passed else "精准提取了沙箱日志中的持久化行为线索"})

    # 4. 验证跨行内存 Dump 解析的特征码 (20分)
    # Target Hex (16 bytes): E8 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF
    expected_sig = "E8112233445566778899AABBCCDDEEFF"
    agent_sig = str(data.get("unpack_signature", "")).strip().upper().replace(" ", "")
    
    if agent_sig == expected_sig:
        details.append({"item": "验证跨行内存裸数据提取 (特征码)", "score": 20, "max_score": 20, "passed": True, "reason": "完美提取了十六进制特征码，成功规避了跨行换行符的干扰"})
    else:
        details.append({"item": "验证跨行内存裸数据提取 (特征码)", "score": 0, "max_score": 20, "passed": False, "reason": f"提取失败，预期: {expected_sig}, 实际: {agent_sig} (可能因正则表达式无法处理跨行导致)"})

    # 5. LLM 校验 CTI 威胁情报接口查询结果 (20分)
    # 考察 Agent 是否成功处理了 401 失败并获取了真正的归属信息，而不是填入了错误提示语
    agent_family = str(data.get("ransomware_family", "")).strip()
    
    if not agent_family or "error" in agent_family.lower() or "401" in agent_family:
        details.append({"item": "利用大模型验证勒索软件家族名称的合理性", "score": 0, "max_score": 20, "passed": False, "reason": "获取到的威胁情报值为空，或包含了 API 错误代码"})
    else:
        # LLM 探针：判断提取出的文字是否像一个黑客组织或勒索软件名称
        prompt = "Assess whether the following text represents a valid Ransomware Family name, Threat Actor name, or APT group (e.g., LockBit, Wannacry, APT28, Lazarus, Unknown Ransomware Family, etc.). It should NOT be an API error message, HTTP status code, or random technical JSON dump. If it looks like a valid threat naming convention, output YES. Otherwise, output NO."
        is_valid_family = llm_judge_content(prompt, agent_family)
        
        if is_valid_family:
            details.append({"item": "利用大模型验证勒索软件家族名称的合理性", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定提取出的情报归属信息语义合法"})
        else:
            details.append({"item": "利用大模型验证勒索软件家族名称的合理性", "score": 0, "max_score": 20, "passed": False, "reason": f"大模型判定值 [{agent_family}] 不是一个有效的恶意软件家族名称(可能包含了幻觉或 API 异常抓取)"})

    total_score = sum(d["score"] for d in details)
    return total_score, details

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    final_score, result_details = verify(workspace)
    
    output_data = {
        "total_score": final_score,
        "details": result_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
