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
    """
    此函数为检测非结构化文本的统一接口。
    针对本任务，若需后续拓展评估生成的邮件或自然语言总结报告，必须通过该接口进行判定。
    由于本任务核心为高度结构化的 JSON 提取，主验证逻辑采用代码级硬校验，以保障 0 幻觉和防作弊。
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    
    target_json_path = os.path.join(workspace, "iocs", "extracted_iocs.json")
    
    # 【1. 检查结果文件是否存在】 - 10分
    if os.path.exists(target_json_path):
        results.append({"item": "检查目标输出文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到了 iocs/extracted_iocs.json"})
        total_score += 10
    else:
        results.append({"item": "检查目标输出文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 iocs/extracted_iocs.json"})
        
    data = None
    if os.path.exists(target_json_path):
        try:
            with open(target_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            pass
            
    # 【2. 检查数据 Schema 与是否剔除捏造字段】 - 10分
    if data is not None and isinstance(data, dict):
        required_keys = {"registry_value", "malicious_path", "unpack_signature"}
        found_keys = set(data.keys())
        if required_keys.issubset(found_keys):
            if len(found_keys) == 3:
                results.append({"item": "检查 JSON Schema", "score": 10, "max_score": 10, "passed": True, "reason": "包含且仅包含规定的三个顶层键"})
                total_score += 10
            else:
                # 严惩幻觉：Agent捏造了不相关的字段
                results.append({"item": "检查 JSON Schema", "score": 5, "max_score": 10, "passed": False, "reason": f"包含了规定的键，但捏造了多余字段: {list(found_keys - required_keys)}"})
                total_score += 5
        else:
            results.append({"item": "检查 JSON Schema", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失规定字段，当前字段列表: {list(found_keys)}"})
    else:
        results.append({"item": "检查 JSON Schema", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 文件无法被正常解析或非对象(dict)结构"})
        
    # 【3. 精准验证: 注册表键值 registry_value】 - 25分
    if data and "registry_value" in data:
        reg_val = str(data.get("registry_value", "")).strip()
        if reg_val == "WinUpdateSvc_9110":
            results.append({"item": "验证注册表持久化键名提取", "score": 25, "max_score": 25, "passed": True, "reason": "精确匹配到 WinUpdateSvc_9110"})
            total_score += 25
        else:
            results.append({"item": "验证注册表持久化键名提取", "score": 0, "max_score": 25, "passed": False, "reason": f"匹配失败，预期 'WinUpdateSvc_9110'，实际提取内容为: '{reg_val}'"})
    else:
        results.append({"item": "验证注册表持久化键名提取", "score": 0, "max_score": 25, "passed": False, "reason": "未提取到 registry_value 字段"})

    # 【4. 精准验证: 恶意载荷路径 malicious_path】 - 25分
    if data and "malicious_path" in data:
        mal_path = str(data.get("malicious_path", "")).strip()
        # 处理可能的 JSON 字符串转义造成的斜杠重叠差异
        normalized_path = mal_path.replace("\\\\", "\\")
        if normalized_path == "C:\\Users\\Public\\svchost_mal.exe":
            results.append({"item": "验证恶意载荷路径提取", "score": 25, "max_score": 25, "passed": True, "reason": "精确匹配到 C:\\Users\\Public\\svchost_mal.exe"})
            total_score += 25
        else:
            results.append({"item": "验证恶意载荷路径提取", "score": 0, "max_score": 25, "passed": False, "reason": f"匹配失败，实际提取内容为: '{mal_path}'"})
    else:
        results.append({"item": "验证恶意载荷路径提取", "score": 0, "max_score": 25, "passed": False, "reason": "未提取到 malicious_path 字段"})

    # 【5. 复杂解析验证: 脱壳特征码提取 unpack_signature】 - 30分
    if data and "unpack_signature" in data:
        sig = str(data.get("unpack_signature", "")).strip().upper()
        # 强制将空字符或连字符过滤，应对 Agent 小作弊
        sig = sig.replace(" ", "").replace("-", "")
        # 正确签名应紧跟在 4D 5A 后的连续 16 字节
        expected_sig = "1A2B3C4D5E6F708192A3B4C5D6E7F809"
        
        if sig == expected_sig:
            results.append({"item": "验证深层脱壳十六进制特征码还原提取", "score": 30, "max_score": 30, "passed": True, "reason": "完美过滤 Dump 噪音并精确定位 4D 5A 后的 16 字节特征码"})
            total_score += 30
        else:
            results.append({"item": "验证深层脱壳十六进制特征码还原提取", "score": 0, "max_score": 30, "passed": False, "reason": f"特征码提取不正确，实际值为: '{sig}'"})
    else:
        results.append({"item": "验证深层脱壳十六进制特征码还原提取", "score": 0, "max_score": 30, "passed": False, "reason": "未提取到 unpack_signature 字段"})

    # 汇总得分记录
    output_data = {
        "total_score": total_score,
        "details": results
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
