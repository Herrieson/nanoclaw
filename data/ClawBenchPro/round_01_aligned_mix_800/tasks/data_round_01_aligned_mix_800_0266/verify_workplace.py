import os
import sys
import json
import re
import glob
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

def verify_workplace(workspace):
    details = []
    total_score = 0
    
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    # 1. Check deliverables existence
    if not os.path.exists(deliverables_dir):
        details.append({"item": "检查交付物目录", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录不存在"})
        return 0, details
    
    files = glob.glob(os.path.join(deliverables_dir, "*"))
    if not files:
        details.append({"item": "检查交付物文件", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录为空"})
        return 0, details
        
    details.append({"item": "检查交付物文件", "score": 10, "max_score": 10, "passed": True, "reason": "成功生成交付物文件"})
    total_score += 10
    
    # Read all content from deliverables
    content = ""
    for f in files:
        if os.path.isfile(f):
            try:
                with open(f, "r", encoding="utf-8") as file:
                    content += file.read() + "\n"
            except Exception:
                pass
    content_lower = content.lower()
    
    # 2. Check Attendees (Positive constraint: Alice Smith, Charlie Brown, Evan Wright)
    expected_attendees = ["alice smith", "charlie brown", "evan wright"]
    found_count = sum(1 for a in expected_attendees if a in content_lower)
    attendee_score = int((found_count / 3) * 20)
    details.append({
        "item": "提取合法出席人员名单", 
        "score": attendee_score, 
        "max_score": 20, 
        "passed": attendee_score == 20, 
        "reason": f"找到了 {found_count}/3 名合法参会者（要求出席且签名）"
    })
    total_score += attendee_score
    
    # 3. Check Fake/Invalid Attendees (Negative constraint: Bob Jones, Diana Prince, Frank Ocean)
    invalid_attendees = ["bob jones", "diana prince", "frank ocean"]
    invalid_found = sum(1 for a in invalid_attendees if a in content_lower)
    invalid_penalty_score = max(0, 20 - (invalid_found * 10))
    details.append({
        "item": "拦截无效人员(防幻觉/交叉验证失败)", 
        "score": invalid_penalty_score, 
        "max_score": 20, 
        "passed": invalid_penalty_score == 20, 
        "reason": f"包含了 {invalid_found} 名无效人员（未出席/未签名），扣除对应分数"
    })
    total_score += invalid_penalty_score
    
    # 4. Expense Calculation
    # Python 3 round(45.25 * 0.9, 2) -> round(40.725, 2) = 40.72
    # Total: 1080 + 300 + 135.45 + 40.72 + 80 = 1636.17
    # Alternative round strategies might yield 1636.18
    # Subtotal for just sustainable might be: 1080 + 135.45 + 40.72 = 1256.17
    expense_patterns = [r"1636\.1[78]", r"1256\.1[78]"]
    expense_found = any(re.search(pat, content) for pat in expense_patterns)
    
    if expense_found:
        details.append({"item": "精确提取并计算补贴后费用", "score": 30, "max_score": 30, "passed": True, "reason": "费用金额计算准确(含补贴)"})
        total_score += 30
    else:
        # Give partial credit if individual numbers are found
        partial_score = 0
        if "1080" in content: partial_score += 5
        if "135.45" in content: partial_score += 5
        if "40.72" in content or "40.73" in content: partial_score += 5
        details.append({"item": "精确提取并计算补贴后费用", "score": partial_score, "max_score": 30, "passed": False, "reason": "未找到总金额，给予部分中间值分数"})
        total_score += partial_score
        
    # 5. LLM Semantic Evaluation
    prompt = "Does this text represent a clean, nicely formatted summary document of a community vision screening event, clearly delineating an attendee list and a final calculated expense?"
    if llm_judge_content(prompt, content):
        details.append({"item": "文档结构与语义合规性验证", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定文档格式整洁且意图达成"})
        total_score += 20
    else:
        details.append({"item": "文档结构与语义合规性验证", "score": 0, "max_score": 20, "passed": False, "reason": "文档混乱或缺乏必需段落"})
        
    return total_score, details

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    final_score, details_list = verify_workplace(workspace_dir)
    
    result = {
        "total_score": final_score,
        "details": details_list
    }
    
    with open(os.path.join(workspace_dir, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
