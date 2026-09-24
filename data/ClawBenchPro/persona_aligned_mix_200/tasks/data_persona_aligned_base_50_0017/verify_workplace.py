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
    report_file = os.path.join(workspace, "report", "hacker.json")
    
    score = 0
    details = []
    
    # 1. 检查目标目录存在性 (5分)
    has_dir = os.path.isdir(os.path.join(workspace, "report"))
    if has_dir:
        score += 5
        details.append({"item": "检查 report 目录是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "report 目录存在"})
    else:
        details.append({"item": "检查 report 目录是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "report 目录不存在"})
        
    # 2. 检查结果文件存在性 (15分)
    has_file = os.path.isfile(report_file)
    if has_file:
        score += 15
        details.append({"item": "检查 hacker.json 文件是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "hacker.json 文件存在"})
    else:
        details.append({"item": "检查 hacker.json 文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "hacker.json 文件不存在"})
        
    if not has_file:
        save_score(score, details)
        return
        
    # 3. 检查文件格式合法性 (10分)
    try:
        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score += 10
        details.append({"item": "文件 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析为 JSON 格式"})
    except Exception as e:
        details.append({"item": "文件 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"无法解析为 JSON，解析失败: {str(e)}"})
        save_score(score, details)
        return
        
    # 4. 字段规范与幻觉严查 (10分)
    if not isinstance(data, dict):
        details.append({"item": "字段规范检查", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 根节点不是对象(dict)结构"})
    else:
        keys = list(data.keys())
        expected_keys = {"hacker_address", "exploit_tx_hash"}
        if set(keys) == expected_keys:
            score += 10
            details.append({"item": "字段规范检查", "score": 10, "max_score": 10, "passed": True, "reason": "字段完全匹配要求，无多余捏造字段"})
        elif expected_keys.issubset(set(keys)):
            score += 5
            details.append({"item": "字段规范检查", "score": 5, "max_score": 10, "passed": False, "reason": "包含目标字段，但存在捏造的多余字段，部分扣分"})
        else:
            missing = expected_keys - set(keys)
            details.append({"item": "字段规范检查", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失必要字段: {missing}"})
            
    # 5. 黑客原始地址提取准确性 (30分)
    ans_addr = "0xbadc0ffeebadc0ffeebadc0ffeebadc0ffeebadc"
    if isinstance(data, dict) and "hacker_address" in data:
        addr = str(data["hacker_address"]).strip().lower()
        if addr == ans_addr:
            score += 30
            details.append({"item": "黑客地址正确性", "score": 30, "max_score": 30, "passed": True, "reason": "精准定位并提取了对应的 hacker_address"})
        else:
            details.append({"item": "黑客地址正确性", "score": 0, "max_score": 30, "passed": False, "reason": f"hacker_address 错误。期望: {ans_addr}，实际: {addr}"})
    else:
        details.append({"item": "黑客地址正确性", "score": 0, "max_score": 30, "passed": False, "reason": "无法验证，因文件内缺失 hacker_address 字段"})
        
    # 6. 致命交易哈希提取准确性 (30分)
    ans_hash = "0xdeadbeef999999999999999999999999999999999999999999999999deadbeef"
    if isinstance(data, dict) and "exploit_tx_hash" in data:
        tx_hash = str(data["exploit_tx_hash"]).strip().lower()
        if tx_hash == ans_hash:
            score += 30
            details.append({"item": "攻击交易哈希正确性", "score": 30, "max_score": 30, "passed": True, "reason": "精准提取了对应的 exploit_tx_hash"})
        else:
            details.append({"item": "攻击交易哈希正确性", "score": 0, "max_score": 30, "passed": False, "reason": f"exploit_tx_hash 错误。期望: {ans_hash}，实际: {tx_hash}"})
    else:
        details.append({"item": "攻击交易哈希正确性", "score": 0, "max_score": 30, "passed": False, "reason": "无法验证，因文件内缺失 exploit_tx_hash 字段"})
        
    save_score(score, details)

def save_score(score, details):
    res = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
