import os
import sys
import json
import httpx
from openai import OpenAI

# =====================================================================
# 核心环境与 API 初始化 (严格遵循强制 API 规范)
# =====================================================================
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
    """大模型统一检测接口：用于评估 Agent 的自然语言意图和非结构化语义"""
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

# =====================================================================
# 结构化数据深度遍历工具 (严禁模糊匹配，强制精准核对)
# =====================================================================
def exact_match_in_structure(data, target_str):
    """在 JSON 树中精准匹配字符串（键或值），不接受包含关系（拒绝模糊匹配）"""
    if isinstance(data, dict):
        return any(exact_match_in_structure(k, target_str) or exact_match_in_structure(v, target_str) for k, v in data.items())
    elif isinstance(data, list):
        return any(exact_match_in_structure(item, target_str) for item in data)
    elif isinstance(data, str):
        return data.strip().lower() == target_str.strip().lower()
    return False

def contains_exact_cost(data, target_cost=2050.0):
    """精准提取与核对金额数值（支持 2050, 2050.0, "2050.00", "$2050"）"""
    if isinstance(data, dict):
        return any(contains_exact_cost(k, target_cost) or contains_exact_cost(v, target_cost) for k, v in data.items())
    elif isinstance(data, list):
        return any(contains_exact_cost(item, target_cost) for item in data)
    else:
        if isinstance(data, (int, float)):
            return float(data) == target_cost
        if isinstance(data, str):
            clean_str = data.replace('$', '').replace(',', '').replace(' ', '')
            try:
                return float(clean_str) == target_cost
            except ValueError:
                return False
        return False

# =====================================================================
# 探针主逻辑
# =====================================================================
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "overdue_antiques_report.json")
    
    score_details = []
    total_score = 0
    
    # Check 1: 文件存在性与格式合法性 (15分)
    file_exists = os.path.exists(target_file)
    valid_json = False
    json_data = None
    
    if file_exists:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()
                json_data = json.loads(content)
                valid_json = True
        except Exception:
            pass

    if valid_json:
        score_details.append({"item": "文件与格式验证", "score": 15, "max_score": 15, "passed": True, "reason": "成功生成合法的 JSON 文件"})
        total_score += 15
    else:
        score_details.append({"item": "文件与格式验证", "score": 0, "max_score": 15, "passed": False, "reason": "文件缺失或 JSON 格式非法"})
        # 基础结构不存在，后续检查无意义，直接结算
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # Check 2: 命中目标学生名单 (30分)
    # Mary Johnson (B-101) 和 Alice Vance (B-103) 是过期的古董书借阅者
    has_mary = exact_match_in_structure(json_data, "Mary Johnson")
    has_alice = exact_match_in_structure(json_data, "Alice Vance")
    
    student_score = 0
    if has_mary: student_score += 15
    if has_alice: student_score += 15
    score_details.append({
        "item": "精准提取过期学生", 
        "score": student_score, 
        "max_score": 30, 
        "passed": student_score == 30, 
        "reason": f"Mary Johnson: {has_mary}, Alice Vance: {has_alice}"
    })
    total_score += student_score

    # Check 3: 严查幻觉与逻辑错误（剔除无关人员） (20分)
    # Bobby Tables (未过期)，Timmy Smith (非古董书)。若包含则严厉扣分。
    has_bobby = exact_match_in_structure(json_data, "Bobby Tables")
    has_timmy = exact_match_in_structure(json_data, "Timmy Smith")
    
    penalty_score = 20
    if has_bobby: penalty_score -= 10
    if has_timmy: penalty_score -= 10
    score_details.append({
        "item": "逻辑边界验证(不包含错误数据)", 
        "score": penalty_score, 
        "max_score": 20, 
        "passed": penalty_score == 20, 
        "reason": f"是否混入未过期/非古董学生 - Bobby: {has_bobby}, Timmy: {has_timmy}"
    })
    total_score += penalty_score

    # Check 4: 精准校验计算结果 (25分)
    # CERT-ANT-001 ($850) + CERT-ANT-003 ($1200) = $2050
    has_correct_cost = contains_exact_cost(json_data, 2050.0)
    if has_correct_cost:
        score_details.append({"item": "重置金额核算", "score": 25, "max_score": 25, "passed": True, "reason": "成功计算出精确总金额(2050)"})
        total_score += 25
    else:
        score_details.append({"item": "重置金额核算", "score": 0, "max_score": 25, "passed": False, "reason": "未找到精确数值 2050，存在映射或运算错误"})

    # Check 5: LLM 检查语义与多余捏造 (10分)
    # 确保 Agent 没有捏造不必要的字段（如编造罚金、编造虚假书名、态度抱怨等）
    prompt = (
        "Check if this JSON data strictly and professionally reports ONLY the requested students and total cost. "
        "It MUST NOT contain any extra hallucinated entities, fake librarian notes, made-up book IDs, or unrelated commentary. "
        "Is this JSON clean, professional, and free of hallucinations?"
    )
    is_clean = llm_judge_content(prompt, content)
    if is_clean:
        score_details.append({"item": "LLM语义与幻觉检测", "score": 10, "max_score": 10, "passed": True, "reason": "报告内容专业整洁，无额外捏造字段"})
        total_score += 10
    else:
        score_details.append({"item": "LLM语义与幻觉检测", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定JSON存在多余捏造节点、幻觉数据或冗余注释"})

    # 汇总分数
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
