import os
import sys
import json
import httpx
from openai import OpenAI

# =====================================================================
# 核心检测原则： Workplace (结果域探针)
# 1. 代码负责确定性文件结构、JSON Schema 与精准提取 IoC (入侵指标) 值。
# 2. 严禁模糊正则匹配；采用严格去噪标准化对比。
# 3. LLM 负责语义验证：检查提取结果是否无幻觉且符合业务逻辑要求。
# =====================================================================

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型进行语义与幻觉检测统一接口"""
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

def normalize_path(s):
    """规范化路径：统一小写并使用正斜杠"""
    return str(s).lower().replace("\\", "/")

def normalize_hex(s):
    """规范化特征码：统一大写并剔除所有空格"""
    return str(s).upper().replace(" ", "")

def extract_all_strings(data):
    """递归提取 JSON 中的所有标量字符串值，以便精确定位"""
    strings = []
    if isinstance(data, dict):
        for k, v in data.items():
            strings.append(str(k))
            strings.extend(extract_all_strings(v))
    elif isinstance(data, list):
        for item in data:
            strings.extend(extract_all_strings(item))
    elif isinstance(data, str):
        strings.append(data)
    elif isinstance(data, (int, float)):
        strings.append(str(data))
    return strings

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "report", "ioc.json")

    score_details = []
    total_score = 0
    json_data = None

    # =======================================================
    # 检查项 1：文件存在性及 JSON Schema 合法性 (20 分)
    # =======================================================
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            score_details.append({
                "item": "检查 report/ioc.json 文件存在性及 JSON 格式",
                "score": 20, "max_score": 20, "passed": True,
                "reason": "文件存在且 JSON 格式合法解析通过。"
            })
            total_score += 20
        except Exception as e:
            score_details.append({
                "item": "检查 report/ioc.json 文件存在性及 JSON 格式",
                "score": 0, "max_score": 20, "passed": False,
                "reason": f"解析 JSON 失败或文件读取异常：{e}"
            })
    else:
        score_details.append({
            "item": "检查 report/ioc.json 文件存在性及 JSON 格式",
            "score": 0, "max_score": 20, "passed": False,
            "reason": "报告文件报告不存在于指定目录。"
        })

    # 提取所有数据用于代码严谨比对
    all_strings = extract_all_strings(json_data) if json_data else []

    # =======================================================
    # 检查项 2：精准数值提取 - 恶意可执行文件路径 (20 分)
    # =======================================================
    target_path = "c:/programdata/intel/telemetry_srv.exe"
    path_found = any(target_path in normalize_path(s) for s in all_strings)
    
    if path_found:
        score_details.append({
            "item": "利用确定性逻辑提取目标恶意文件路径 IoC",
            "score": 20, "max_score": 20, "passed": True,
            "reason": "JSON 中准确包含了经过注册表追溯得到的后门路径。"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "利用确定性逻辑提取目标恶意文件路径 IoC",
            "score": 0, "max_score": 20, "passed": False,
            "reason": "未找到匹配的可执行文件路径，TAS 日志分析可能失败。"
        })

    # =======================================================
    # 检查项 3：精准数值提取 - 16 字节十六进制特征码 (20 分)
    # =======================================================
    target_hex = "5C7A8E1F2B3D4C5A6B7C8D9EAFB0C1D2"
    hex_found = any(target_hex in normalize_hex(s) for s in all_strings)

    if hex_found:
        score_details.append({
            "item": "利用确定性逻辑提取 16 字节内存脱壳特征码 IoC",
            "score": 20, "max_score": 20, "passed": True,
            "reason": "JSON 中准确包含了利用 Volatility 插件提取出的 Payload 特征码。"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "利用确定性逻辑提取 16 字节内存脱壳特征码 IoC",
            "score": 0, "max_score": 20, "passed": False,
            "reason": "未找到对应的 16 字节 Hex 特征码，或内存 Dump 分析出错。"
        })

    # =======================================================
    # 检查项 4：LLM 语义检测与幻觉防范 (40 分)
    # =======================================================
    prompt_text = """
    The user has provided a JSON report containing Indicators of Compromise (IoC) generated by a security analysis system.
    We expect to see EXACTLY two main indicators explicitly described in the JSON key-value pairs:
    1. A malicious executable path (C:\\ProgramData\\Intel\\telemetry_srv.exe)
    2. A 16-byte unpacket signature (5C 7A 8E 1F 2B 3D 4C 5A 6B 7C 8D 9E AF B0 C1 D2)
    
    Please rigorously verify:
    1. Does the JSON explicitly and clearly map these values to appropriate semantic keys (e.g., 'path', 'signature', 'ioc') so a YARA engine could understand?
    2. STRICT NO-HALLUCINATION RULE: Are there NO completely fabricated extra indicators (like fake IP addresses, fake domains, fake hashes) that were NOT requested?

    If the structure makes sense and there are absolutely NO hallucinatory extra fields, answer 'YES'. Otherwise answer 'NO'.
    """

    if json_data is not None:
        try:
            json_content = json.dumps(json_data, indent=2, ensure_ascii=False)
            if llm_judge_content(prompt_text, json_content):
                score_details.append({
                    "item": "大模型检查 IoC 报告的语义逻辑与防范幻觉",
                    "score": 40, "max_score": 40, "passed": True,
                    "reason": "报告键值语义清晰，未发现捏造的多余安全指标(无幻觉)。"
                })
                total_score += 40
            else:
                score_details.append({
                    "item": "大模型检查 IoC 报告的语义逻辑与防范幻觉",
                    "score": 0, "max_score": 40, "passed": False,
                    "reason": "结构语义含糊不清，或检测到捏造的冗余 IoC 字段(如幻觉的 IP/Hash)。"
                })
        except Exception as e:
            score_details.append({
                "item": "大模型检查 IoC 报告的语义逻辑与防范幻觉",
                "score": 0, "max_score": 40, "passed": False,
                "reason": f"大模型评测执行出错: {e}"
            })
    else:
        score_details.append({
            "item": "大模型检查 IoC 报告的语义逻辑与防范幻觉",
            "score": 0, "max_score": 40, "passed": False,
            "reason": "前置 JSON 破损，无法进行语义检测。"
        })

    # =======================================================
    # 结果输出
    # =======================================================
    result = {
        "total_score": total_score,
        "details": score_details
    }

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
