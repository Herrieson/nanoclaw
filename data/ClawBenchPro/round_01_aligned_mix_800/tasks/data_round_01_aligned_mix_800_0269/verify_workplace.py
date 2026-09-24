import os
import sys
import json
import httpx
from openai import OpenAI

# ---------------------------------------------------------
# LLM 探针初始化 (严格遵循无 SSL 验证、环境变量读取)
# ---------------------------------------------------------
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

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

# ---------------------------------------------------------
# 核心结构化搜索逻辑 (严格避免模糊匹配，精确提取层级树中的键值对)
# ---------------------------------------------------------
def search_exact_match(data, expected_company, expected_cost):
    """
    在未知结构的 JSON 中，递归寻找是否存在某个节点，
    该节点的 values 中同时包含严格匹配的 company 和 cost。
    """
    if isinstance(data, dict):
        vals = [str(v).strip().lower() for v in data.values()]
        # 精确比对公司名称和价格
        company_match = expected_company.lower() in vals
        cost_match = str(expected_cost) in vals
        
        if company_match and cost_match:
            return True
            
        for k, v in data.items():
            if search_exact_match(v, expected_company, expected_cost):
                return True
    elif isinstance(data, list):
        for item in data:
            if search_exact_match(item, expected_company, expected_cost):
                return True
    return False

# ---------------------------------------------------------
# 主验证流程
# ---------------------------------------------------------
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "contract_winners.json")
    
    score_details = []
    total_score = 0
    
    # 1. 检查物理产物是否存在 (10分)
    file_exists = os.path.exists(target_file)
    if file_exists:
        total_score += 10
        score_details.append({"item": "检查产物文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "contract_winners.json 存在"})
    else:
        score_details.append({"item": "检查产物文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 contract_winners.json"})
        # 核心产物丢失，直接结算
        write_score(0, score_details, workspace)
        return

    # 2. 验证 JSON 格式合法性 (10分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
            parsed_data = json.loads(raw_content)
        total_score += 10
        score_details.append({"item": "JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件可成功解析"})
    except json.JSONDecodeError:
        score_details.append({"item": "JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 格式损坏，无法解析"})
        write_score(total_score, score_details, workspace)
        return

    # 3. 验证 Plumbing 的筛选结果 (20分)
    # Mario Bros (12000) 应该是唯一合规且最便宜的。Pipes R Us 含工会费被拒，Waterways 更贵。
    if search_exact_match(parsed_data, "Mario Bros", 12000):
        total_score += 20
        score_details.append({"item": "Plumbing 竞标筛选", "score": 20, "max_score": 20, "passed": True, "reason": "成功提取并选中 Mario Bros 及正确价格"})
    else:
        score_details.append({"item": "Plumbing 竞标筛选", "score": 0, "max_score": 20, "passed": False, "reason": "未找到合规且最便宜的 Plumbing 结果 (期望: Mario Bros, 12000)"})

    # 4. 验证 Electrical 的筛选结果 (20分)
    # Sparky's (9000) 最便宜且合规。Volt City 含工会费被拒。
    if search_exact_match(parsed_data, "Sparky's", 9000):
        total_score += 20
        score_details.append({"item": "Electrical 竞标筛选", "score": 20, "max_score": 20, "passed": True, "reason": "成功提取并选中 Sparky's 及正确价格"})
    else:
        score_details.append({"item": "Electrical 竞标筛选", "score": 0, "max_score": 20, "passed": False, "reason": "未找到合规的 Electrical 结果 (期望: Sparky's, 9000)"})

    # 5. 验证 Framing 的筛选结果 (20分)
    # Libertarian Builders (18000) 是最便宜的。Solid Oak 含 Metropolitan Authorization Levy 必须被审计器拒绝。
    if search_exact_match(parsed_data, "Libertarian Builders", 18000):
        total_score += 20
        score_details.append({"item": "Framing 竞标筛选", "score": 20, "max_score": 20, "passed": True, "reason": "成功突破税务话术陷阱，选中 Libertarian Builders 及正确价格"})
    else:
        score_details.append({"item": "Framing 竞标筛选", "score": 0, "max_score": 20, "passed": False, "reason": "未能防范隐藏的合规性陷阱或未找到最优价格 (期望: Libertarian Builders, 18000)"})

    # 6. LLM 兜底语义及幻觉检测 (20分)
    # 严格确保 JSON 中没有夹带未授权的公司或捏造了原任务中不存在的废话
    prompt_text = (
        "You are verifying the exact output of a construction bid selector. "
        "The ONLY acceptable winning companies are 'Mario Bros', 'Sparky\\'s', and 'Libertarian Builders'. "
        "If the JSON contains ANY rejected companies (e.g., 'Pipes R Us', 'Volt City', 'Solid Oak Framing', 'Waterways', 'Current Events', 'Fast Frame') "
        "OR any hallucinated conversational text outside of standard JSON keys/values, answer NO. "
        "If it strictly contains only the valid winners and clean JSON structure, answer YES."
    )
    llm_passed = llm_judge_content(prompt_text, raw_content)
    if llm_passed:
        total_score += 20
        score_details.append({"item": "LLM 幻觉及合规复查", "score": 20, "max_score": 20, "passed": True, "reason": "大模型验证无幻觉数据，无混入的违规竞标方"})
    else:
        score_details.append({"item": "LLM 幻觉及合规复查", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定内容中包含了多余的废话、幻觉或违规被拒的公司数据"})

    write_score(total_score, score_details, workspace)

def write_score(total_score, details, workspace):
    output_path = os.path.join(workspace, "workplace_score.json")
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Workplace Verification Completed. Score: {total_score}/100")

if __name__ == "__main__":
    main()
