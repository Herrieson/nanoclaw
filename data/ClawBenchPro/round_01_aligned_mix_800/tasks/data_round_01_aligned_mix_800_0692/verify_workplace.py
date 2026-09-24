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
    """用于检测非结构化文本/复杂自定义结构的统一大模型接口"""
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

def extract_all_text(obj):
    """递归提取 JSON 中的所有键和值，转化为小写字符串，用于严格的代码层面的基础判定"""
    texts = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            texts.append(str(k).lower().strip())
            texts.extend(extract_all_text(v))
    elif isinstance(obj, list):
        for v in obj:
            texts.extend(extract_all_text(v))
    else:
        texts.append(str(obj).lower().strip())
    return texts

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "overdue_antiques_report.json")
    
    details = []
    total_score = 0
    
    # 1. 检查结果文件是否存在 (10分)
    exists = os.path.exists(report_path)
    if exists:
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到 overdue_antiques_report.json 文件"})
        total_score += 10
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 overdue_antiques_report.json 文件"})
        
    json_data = None
    if exists:
        # 2. 原生代码严谨校验 JSON Schema 格式 (20分)
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            details.append({"item": "代码检测：文件是否为合法JSON格式", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 解析成功，格式合法"})
            total_score += 20
        except Exception as e:
            details.append({"item": "代码检测：文件是否为合法JSON格式", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON 解析失败，文件可能遭到损坏或混入非法字符: {e}"})
            
    if json_data is not None:
        all_texts = extract_all_text(json_data)
        
        # 确定性查找：核心指标是否存在
        has_mary = any("mary" in t for t in all_texts)
        has_alice = any("alice" in t for t in all_texts)
        has_2050 = any("2050" in t for t in all_texts)
        
        # 3. 原生代码严谨校验：关键数据点提取 (15分)
        if has_mary and has_alice:
            details.append({"item": "代码检测：核心学生名单提取", "score": 15, "max_score": 15, "passed": True, "reason": "成功在 JSON 中提取到 Mary 和 Alice 的节点信息"})
            total_score += 15
        else:
            details.append({"item": "代码检测：核心学生名单提取", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 的键值中缺失 Mary 或 Alice，名单不全"})
            
        # 4. 原生代码严谨校验：核心数值计算 (15分)
        if has_2050:
            details.append({"item": "代码检测：总金额精准匹配", "score": 15, "max_score": 15, "passed": True, "reason": "成功在 JSON 中精准匹配到计算结果 2050"})
            total_score += 15
        else:
            details.append({"item": "代码检测：总金额精准匹配", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 中未发现总金额 2050 (Mary $850 + Alice $1200)，发生幻觉或计算错误"})
            
        # 5. 大模型语义检测：非结构化/自定义 Schema 的业务逻辑校验 (40分)
        # 防止假阴性/假阳性：由于题目允许Agent自由设定JSON格式，Agent可能会把未逾期的 Bobby 也写进去并标记为 "not_overdue"。
        # 因此，代码已确认要素存在后，交由 LLM 进行纯粹的业务语义判断。
        formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
        prompt = (
            "Analyze this JSON report regarding overdue antique books. Answer carefully:\n"
            "1. Does it logically attribute overdue status/fines ONLY to 'Mary' (Mary Johnson) and 'Alice' (Alice Vance)?\n"
            "2. Does it clearly indicate a final total replacement cost of exactly $2050?\n"
            "3. Crucially, it must NOT present 'Bobby', 'Sarah', or 'Timmy' as having overdue antique books. (If it tracks them as 'not overdue' in a separate structure, that is acceptable, but they must NOT be in the penalty/overdue list).\n"
            "Does this JSON strictly and logically fulfill ALL the above semantic conditions?"
        )
        llm_pass = llm_judge_content(prompt, formatted_json)
        if llm_pass:
            details.append({"item": "大模型语义检测：业务逻辑与白名单过滤", "score": 40, "max_score": 40, "passed": True, "reason": "大模型判定 JSON 语义结构完美，准确过滤了未逾期（Bobby）和非古董（Sarah）的干扰项，且总金额语义指向明确"})
            total_score += 40
        else:
            details.append({"item": "大模型语义检测：业务逻辑与白名单过滤", "score": 0, "max_score": 40, "passed": False, "reason": "大模型判定 JSON 语义错误，可能将 Bobby/Sarah 错误计入逾期名单，或逻辑指代不明"})
    else:
        # 如果 JSON 不合法，后续代码与语义测试全部跳过得 0 分
        details.append({"item": "代码检测：核心学生名单提取", "score": 0, "max_score": 15, "passed": False, "reason": "文件非合法JSON，无法解析"})
        details.append({"item": "代码检测：总金额精准匹配", "score": 0, "max_score": 15, "passed": False, "reason": "文件非合法JSON，无法解析"})
        details.append({"item": "大模型语义检测：业务逻辑与白名单过滤", "score": 0, "max_score": 40, "passed": False, "reason": "文件非合法JSON，无法进行语义检测"})
        
    # 输出统一格式成绩单
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
