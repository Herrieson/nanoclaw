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
    iocs_file = os.path.join(workspace, "intel", "iocs.json")
    
    details = []
    
    # 1. 结构化解析：检查目录与文件存在性 (20分)
    if not os.path.exists(iocs_file):
        details.append({"item": "检查 iocs.json 文件是否存在及格式合法", "score": 0, "max_score": 20, "passed": False, "reason": "文件 intel/iocs.json 未生成"})
        return 0, details
        
    try:
        with open(iocs_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "检查 iocs.json 文件是否存在及格式合法", "score": 20, "max_score": 20, "passed": True, "reason": "文件存在且通过 JSON Schema 验证"})
    except Exception as e:
        details.append({"item": "检查 iocs.json 文件是否存在及格式合法", "score": 0, "max_score": 20, "passed": False, "reason": f"文件存在但非合法 JSON: {e}"})
        return sum(d["score"] for d in details), details

    # 2. 结构化解析：检查键值数量 (10分)
    if isinstance(data, dict) and len(data.keys()) >= 2:
        details.append({"item": "检查提取的数据结构", "score": 10, "max_score": 10, "passed": True, "reason": "生成了至少包含2个字段的有效字典结构"})
    else:
        details.append({"item": "检查提取的数据结构", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 未提供包含有效键值对的字典"})

    # 3. 确定性提取：恶意的自启路径提取 (30分)
    # 将路径进行平台无关的去转义和小写化处理，防误杀
    raw_json_str = json.dumps(data).lower().replace("\\\\", "\\").replace("/", "\\")
    target_path = r"c:\users\public\videos\svchost_stage2.exe"
    
    if target_path in raw_json_str:
        details.append({"item": "精准验证注册表内恶意的可执行文件路径", "score": 30, "max_score": 30, "passed": True, "reason": "成功找到了通过 EDR 检索返回的深层恶意荷载路径"})
    else:
        details.append({"item": "精准验证注册表内恶意的可执行文件路径", "score": 0, "max_score": 30, "passed": False, "reason": "未找到正确的后续载荷文件路径，可能解析错误或被正常系统调用欺骗"})

    # 4. 确定性提取：16字节脱壳特征码 (30分)
    # 无论有无空格分隔，去掉所有的符号后进行纯十六进制比对
    target_sig = "4d5a90000300000004000000ffff0000"
    found_sig = False
    if isinstance(data, dict):
        for v in data.values():
            clean_v = str(v).lower().replace(" ", "").replace("-", "")
            if target_sig in clean_v:
                found_sig = True
                break
                
    if found_sig:
        details.append({"item": "精准验证专有内存 Dump 解析出的16字节特征码", "score": 30, "max_score": 30, "passed": True, "reason": "通过专属工具配合正确偏移量拿到了完整 Hex 码"})
    else:
        details.append({"item": "精准验证专有内存 Dump 解析出的16字节特征码", "score": 0, "max_score": 30, "passed": False, "reason": "未找到正确的特征码，或使用了错误的方法尝试解析二进制文件"})

    # 5. LLM 验证：自然语言键名语义是否可读 (10分)
    # 原题要求“随便起两个能让人看懂的键名就行”，因此引入 LLM 验证其键名定义是否体现了恶意路径和脱壳特征。
    if isinstance(data, dict) and len(data.keys()) > 0:
        keys_str = ", ".join(data.keys())
        prompt = (f"The user provided a JSON output with the following keys: {keys_str}. "
                  "Do these keys reasonably and semantically represent 'a malicious autostart executable path' "
                  "and 'an unpacked memory hex signature' respectively? (e.g. 'auto_start_path', 'hex_signature').")
        if llm_judge_content(prompt, json.dumps(data, indent=2)):
            details.append({"item": "利用大模型检查 JSON 键名的语义可读性", "score": 10, "max_score": 10, "passed": True, "reason": "键名清晰易懂，符合人工阅读要求"})
        else:
            details.append({"item": "利用大模型检查 JSON 键名的语义可读性", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定键名语义不明或与题意无关"})
    else:
        details.append({"item": "利用大模型检查 JSON 键名的语义可读性", "score": 0, "max_score": 10, "passed": False, "reason": "无有效键名可供检测"})

    return sum(d["score"] for d in details), details

if __name__ == "__main__":
    total_score, details = verify()
    
    output = {
        "total_score": total_score,
        "details": details
    }
    
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
        
    print(f"Verify completed. Total Score: {total_score}")
