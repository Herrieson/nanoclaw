import os
import sys
import json
import re
import httpx
from openai import OpenAI

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
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score_details = []
    total_score = 0
    
    # 1. 结构检查：寻找交付物
    has_files = False
    full_text = ""
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        for root, dirs, files in os.walk(deliverables_dir):
            for file in files:
                has_files = True
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        full_text += f.read() + "\n"
                except Exception:
                    pass
    
    if has_files and full_text.strip():
        score_details.append({"item": "生成交付物文件", "score": 10, "max_score": 10, "passed": True, "reason": "成功在 deliverables 目录中找到非空文件。"})
        total_score += 10
    else:
        score_details.append({"item": "生成交付物文件", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录不存在或内容为空。"})
        
    # 2. 核心精确匹配：黄金记录提取率 (Recall) - Order IDs (20分)
    expected_orders = [f"ORD-GLD-{i+8000}" for i in range(10)]
    found_orders = [o for o in expected_orders if o in full_text]
    order_score = len(found_orders) * 2
    total_score += order_score
    score_details.append({
        "item": "成功提取所有目标 Order ID",
        "score": order_score,
        "max_score": 20,
        "passed": order_score == 20,
        "reason": f"成功识别了 {len(found_orders)}/10 个真正符合退款条件的黄金订单。"
    })
    
    # 3. 核心精确匹配：黄金记录提取率 (Recall) - Customer Names (20分)
    expected_names = [f"Golden VIP {i+1}" for i in range(10)]
    found_names = [n for n in expected_names if n in full_text]
    name_score = len(found_names) * 2
    total_score += name_score
    score_details.append({
        "item": "成功提取所有目标 Customer Name",
        "score": name_score,
        "max_score": 20,
        "passed": name_score == 20,
        "reason": f"成功识别了 {len(found_names)}/10 位真正符合退款条件的客户姓名。"
    })
    
    # 4. 严苛剔除：假阳性与噪音惩罚 (Precision) (40分)
    # 彻底禁止 Agent 凭借大模型幻觉或者粗劣条件瞎蒙，出现非目标数据重度惩罚
    noise_orders = re.findall(r'ORD-\d{6}', full_text)      # 环境中的干扰 Order_ID 格式
    noise_names = re.findall(r'User_\d+_Name', full_text)   # 环境中的干扰 Customer 格式
    noise_refs = re.findall(r'TREF-\d{5}-\d+', full_text)   # 原始干扰 Ticket 编号（不应出现在最终名单）
    
    total_noise = len(noise_orders) + len(noise_names) + len(noise_refs)
    noise_deduction = min(total_noise * 10, 40) # 每个错误数据重扣 10 分
    noise_score = 40 - noise_deduction
    
    total_score += noise_score
    score_details.append({
        "item": "逻辑完备无幻觉 (剔除伪造与不合规噪音)",
        "score": noise_score,
        "max_score": 40,
        "passed": noise_score == 40,
        "reason": f"共发现 {total_noise} 个不符合多重退款条件的噪音数据，扣除 {noise_deduction} 分。"
    })
    
    # 5. LLM 语义校验：财务报表的可读性规范 (10分)
    llm_score = 0
    if has_files and len(full_text.strip()) > 10:
        prompt_text = (
            "Examine the document provided. Is it formatted clearly as a professional priority refund list for a finance team, "
            "prominently highlighting 'Customer Names' and 'Order IDs'? "
            "It must NOT be a raw Python/JSON dump, chaotic text logs, or messy raw email exports. "
            "If it is a structured, readable list/table, answer YES."
        )
        # 截取前3000字符防超载
        if llm_judge_content(prompt_text, full_text[:3000]):
            llm_score = 10
            reason = "经 LLM 判定，输出名单排版清晰且符合财务阅读诉求。"
        else:
            reason = "经 LLM 判定，输出格式混乱（如原样抛出 JSON/代码块），不符合业务文档标准。"
    else:
        reason = "缺乏足够的文件内容以供判定格式。"
        
    total_score += llm_score
    score_details.append({
        "item": "利用大模型检查交付物业务排版",
        "score": llm_score,
        "max_score": 10,
        "passed": llm_score == 10,
        "reason": reason
    })
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
