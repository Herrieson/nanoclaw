import os
import sys
import json
import httpx
from openai import OpenAI

# 强制 API 规范：获取环境变量配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证以支持某些沙盒环境的本地 Mock 代理
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型语义检测接口，仅用于验证非结构化/不可确定形式的内容意图"""
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

def verify(workspace):
    score = 0
    details = []

    # 1. 验证目标目录是否存在 (10分)
    reports_dir = os.path.join(workspace, "reports")
    if os.path.isdir(reports_dir):
        score += 10
        details.append({"item": "检查目标结果目录 reports 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "reports 目录存在"})
    else:
        details.append({"item": "检查目标结果目录 reports 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "reports 目录不存在"})
        
    # 2. 验证目标 JSON 文件是否存在 (10分)
    json_path = os.path.join(reports_dir, "bottleneck.json")
    json_exists = os.path.isfile(json_path)
    if json_exists:
        score += 10
        details.append({"item": "检查 bottleneck.json 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "bottleneck.json 文件存在"})
    else:
        details.append({"item": "检查 bottleneck.json 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "bottleneck.json 文件不存在"})

    # 发生缺失则无法进入内容校验
    if not json_exists:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失，无法校验格式"})
        details.append({"item": "精确提取并验证 Entity ID (0x7C9A)", "score": 0, "max_score": 25, "passed": False, "reason": "文件缺失，无法提取验证"})
        details.append({"item": "精确提取并验证 Block Size (16384)", "score": 0, "max_score": 25, "passed": False, "reason": "文件缺失，无法提取验证"})
        details.append({"item": "严查结构化数据作弊/幻觉生成", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失，无法检查结构"})
        details.append({"item": "利用大模型验证 JSON 键名的业务语义", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失，无法校验"})
        return score, details
        
    # 3. 解析验证 JSON 格式的合法性 (10分)
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            content = f.read()
        data = json.loads(content)
        score += 10
        details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式完全合法并成功解析"})
    except Exception as e:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        details.append({"item": "精确提取并验证 Entity ID (0x7C9A)", "score": 0, "max_score": 25, "passed": False, "reason": "解析失败，无法提取"})
        details.append({"item": "精确提取并验证 Block Size (16384)", "score": 0, "max_score": 25, "passed": False, "reason": "解析失败，无法提取"})
        details.append({"item": "严查结构化数据作弊/幻觉生成", "score": 0, "max_score": 10, "passed": False, "reason": "解析失败，无法检查"})
        details.append({"item": "利用大模型验证 JSON 键名的业务语义", "score": 0, "max_score": 10, "passed": False, "reason": "解析失败，无法检查"})
        return score, details

    # 递归提取 JSON 中所有基本元素（键及值），以应对各种未约定的嵌套格式
    primitives = []
    def extract_all(d):
        if isinstance(d, dict):
            for k, v in d.items():
                primitives.append(str(k))
                extract_all(v)
        elif isinstance(d, list):
            for item in d:
                extract_all(item)
        else:
            primitives.append(str(d))
            
    extract_all(data)
    
    # 4. 精确提取并验证 Entity ID (25分)
    eid_found = False
    for p in primitives:
        if p.strip().upper() == "0X7C9A":
            eid_found = True
            break
    if eid_found:
        score += 25
        details.append({"item": "精确提取并验证 Entity ID (0x7C9A)", "score": 25, "max_score": 25, "passed": True, "reason": "使用代码精确在 JSON 结构中匹配到目标 Entity ID"})
    else:
        details.append({"item": "精确提取并验证 Entity ID (0x7C9A)", "score": 0, "max_score": 25, "passed": False, "reason": "严格代码解析下，未发现异常的 Entity ID 数据项"})
        
    # 5. 精确提取并验证 Block Size (25分)
    size_found = False
    for p in primitives:
        if p.strip() == "16384":
            size_found = True
            break
    if size_found:
        score += 25
        details.append({"item": "精确提取并验证 Block Size (16384)", "score": 25, "max_score": 25, "passed": True, "reason": "使用代码精确在 JSON 结构中匹配到异常的内存大小数值 16384"})
    else:
        details.append({"item": "精确提取并验证 Block Size (16384)", "score": 0, "max_score": 25, "passed": False, "reason": "严格代码解析下，未发现目标的内存快照大小数值"})

    # 6. 幻觉与敷衍全量抓取限制惩罚 (10分)
    # 若元素个数大于 15 则可能是直接把整个段落当 string 放进去或者包含大量多余的数据点
    if len(primitives) <= 15:
        score += 10
        details.append({"item": "严查结构化数据作弊/幻觉生成", "score": 10, "max_score": 10, "passed": True, "reason": f"JSON 结构精简专注 (总元素数 {len(primitives)})，无冗余无用捏造"})
    else:
        details.append({"item": "严查结构化数据作弊/幻觉生成", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 规模过于冗杂 (总元素数 {len(primitives)})，可能含有大模型推诿词及未提取的全量内容映射"})

    # 7. LLM 检查非约定语义：键名的业务合理性 (10分)
    keys = []
    if isinstance(data, dict):
        keys = list(data.keys())
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        keys = list(data[0].keys())
        
    if keys:
        prompt = "判断以下的 JSON 键名是否合理地传达了 'Entity ID / EID' 和 'Memory Size / Block Size' 的含义。只要键名能看出来是在表示这两个概念（允许缩写或近义词），回答 YES。如果都是毫无意义的字母（如 a, b, key1, data）或是在答非所问抱怨，回答 NO。"
        keys_str = ", ".join([str(k) for k in keys])
        is_semantic_ok = llm_judge_content(prompt, keys_str)
        if is_semantic_ok:
            score += 10
            details.append({"item": "利用大模型验证 JSON 键名的业务语义", "score": 10, "max_score": 10, "passed": True, "reason": f"大模型认为字典键名 ['{keys_str}'] 符合专业且明确的语义"})
        else:
            details.append({"item": "利用大模型验证 JSON 键名的业务语义", "score": 0, "max_score": 10, "passed": False, "reason": f"大模型认为生成的键名 ['{keys_str}'] 未能有效传达 'Entity ID' 和 '内存大小' 的业务概念"})
    else:
        details.append({"item": "利用大模型验证 JSON 键名的业务语义", "score": 0, "max_score": 10, "passed": False, "reason": "文件结构非标准键值对对象，无法提取 Keys 给 LLM 进行语义判定"})

    return score, details

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score, details = verify(workspace)
    
    result = {
        "total_score": score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
