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
    """用于检测 JSON 的 Key 语义是否符合要求"""
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

def verify_iocs(workspace):
    score_details = []
    total_score = 0
    
    intel_dir = os.path.join(workspace, "intel")
    iocs_file = os.path.join(intel_dir, "iocs.json")
    
    # Item 1: 检查输出文件是否存在 (10分)
    if os.path.isfile(iocs_file):
        score_details.append({"item": "检查 iocs.json 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目标文件 iocs.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 iocs.json 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 intel/iocs.json 文件，缺失所有结果"})
        return total_score, score_details
        
    # Item 2: 检查文件格式是否合法 (10分)
    try:
        with open(iocs_file, "r", encoding="utf-8") as f:
            iocs_data = json.load(f)
        score_details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON 格式"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        return total_score, score_details
        
    if not isinstance(iocs_data, dict):
        score_details.append({"item": "检查 JSON 顶层结构", "score": 0, "max_score": 80, "passed": False, "reason": "JSON 的根节点不是字典/对象结构，无法提取键值对"})
        return total_score, score_details

    # Item 3: 检查键值语义合法性 (10分)
    keys_str = ", ".join(iocs_data.keys())
    prompt = "The provided keys are extracted from a JSON. The task required defining one key for a 'persistence path' (malicious filepath) and another for a 'payload signature' (hex signature). Do the provided keys semantically reflect these two distinct concepts?"
    if llm_judge_content(prompt, keys_str):
        score_details.append({"item": "检查键名语义合法性 (LLM)", "score": 10, "max_score": 10, "passed": True, "reason": f"键名 [{keys_str}] 满足语义清晰的要求"})
        total_score += 10
    else:
        score_details.append({"item": "检查键名语义合法性 (LLM)", "score": 0, "max_score": 10, "passed": False, "reason": f"大模型判定键名 [{keys_str}] 未能准确表达'持久化路径'与'特征码'的语义"})

    # Item 4: 检查恶意路径提取准确性 (30分)
    target_path = r"C:\ProgramData\Microsoft\Network\svchost_stage3.exe"
    target_path_norm = os.path.normcase(target_path).replace("\\", "/")
    
    path_found = False
    for v in iocs_data.values():
        if isinstance(v, str):
            v_norm = os.path.normcase(v).replace("\\", "/")
            if v_norm == target_path_norm:
                path_found = True
                break
                
    if path_found:
        score_details.append({"item": "准确提取恶意自启后门路径", "score": 30, "max_score": 30, "passed": True, "reason": "已找到目标后门路径 svchost_stage3.exe，抗诱饵成功"})
        total_score += 30
    else:
        score_details.append({"item": "准确提取恶意自启后门路径", "score": 0, "max_score": 30, "passed": False, "reason": "未找到正确的后门路径，可能提取了正常进程伪装 (如 Steam/OneDrive) 或完全遗漏"})
        
    # Item 5: 检查内存特征码提取准确性 (40分)
    # 要求：严格的大写、单空格分隔的16字节十六进制，不能附带 ASCII
    target_sig = "4D 5A 90 00 03 00 00 00 04 00 00 00 FF FF 00 00"
    
    sig_found_perfect = False
    sig_found_partial = False
    
    for v in iocs_data.values():
        if isinstance(v, str):
            v_clean_perfect = v.strip()
            # 宽容处理：允许中间有多个空格或包含小写，但绝不许混有非 hex 字符（如 ASCII 的 MZ）
            v_clean_partial = re.sub(r'\s+', ' ', v.strip().upper())
            
            if v_clean_perfect == target_sig:
                sig_found_perfect = True
                break
            elif v_clean_partial == target_sig:
                sig_found_partial = True

    if sig_found_perfect:
        score_details.append({"item": "严格准确提取内存特征码", "score": 40, "max_score": 40, "passed": True, "reason": "准确提取了 16 字节十六进制特征码，且格式完全规范"})
        total_score += 40
    elif sig_found_partial:
        score_details.append({"item": "严格准确提取内存特征码", "score": 25, "max_score": 40, "passed": False, "reason": "提取了正确的特征码，但存在大小写不规范或多余的空格符，未达完美"})
        total_score += 25
    else:
        score_details.append({"item": "严格准确提取内存特征码", "score": 0, "max_score": 40, "passed": False, "reason": "未能提取精确的16字节十六进制特征码，可能包含了附加的 ASCII 字符，或找错了内存基址/偏移量"})

    # Penalty: 惩罚作弊与捏造行为
    if len(iocs_data.keys()) > 3:
        penalty = 20
        total_score = max(0, total_score - penalty)
        score_details.append({"item": "严禁数据捏造与海量倾倒", "score": -penalty, "max_score": 0, "passed": False, "reason": f"JSON内包含 {len(iocs_data.keys())} 个字段，超出了题目要求的两个字段，存在倾倒测试数据的作弊行为"})

    return total_score, score_details

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score, score_details = verify_iocs(workspace)
    
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
