import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

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
    report_path = os.path.join(workspace, "audit_reports", "summary.json")
    
    score_details = []
    total_score = 0
    
    # 1. 检查目录与文件是否存在 (10分)
    if os.path.exists(report_path):
        score_details.append({"item": "检查目标文件生成", "score": 10, "max_score": 10, "passed": True, "reason": "文件 audit_reports/summary.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标文件生成", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 audit_reports/summary.json"})
        
        # 严重错误，直接输出结束
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 读取 JSON 文件
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
            file_content_raw = f.read() # For LLM checking later
    except Exception as e:
        score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. 检查 JSON 字段完整度 (20分)
    has_ghost_stock = "ghost_stock" in report_data
    has_revenue_loss = "total_revenue_loss" in report_data
    if has_ghost_stock and has_revenue_loss:
        score_details.append({"item": "检查 JSON 字段完整度", "score": 20, "max_score": 20, "passed": True, "reason": "包含所需的核心字段"})
        total_score += 20
    else:
        score_details.append({"item": "检查 JSON 字段完整度", "score": 0, "max_score": 20, "passed": False, "reason": "缺失 ghost_stock 或 total_revenue_loss 字段"})

    # 3. 严格检查 Ghost Stock 的准确性 (30分)
    if has_ghost_stock:
        ghost_stock_list = report_data.get("ghost_stock", [])
        if isinstance(ghost_stock_list, list):
            extracted_items = set()
            for item in ghost_stock_list:
                if isinstance(item, dict) and "item_id" in item:
                    extracted_items.add(item["item_id"])
            
            # 正确答案: 过滤掉脏数据(-5)后，PUMP不缺；累加重复项(50+50=100)后，VALVE不缺。只有 DRILL-X (15 vs 5) 和 TRACTOR-09 (1 vs 0) 缺失。
            expected_items = {"DRILL-X", "TRACTOR-09"}
            
            if extracted_items == expected_items:
                score_details.append({"item": "检查幽灵库存计算准确性", "score": 30, "max_score": 30, "passed": True, "reason": "精准找出了 DRILL-X 和 TRACTOR-09，说明正确处理了 CSV 脏数据"})
                total_score += 30
            else:
                score_details.append({"item": "检查幽灵库存计算准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"计算错误，预期包含 {expected_items}，实际得到 {extracted_items}。可能未能正确清洗 CSV 负数或合并重复项。"})
        else:
            score_details.append({"item": "检查幽灵库存计算准确性", "score": 0, "max_score": 30, "passed": False, "reason": "ghost_stock 必须是包含字典的列表"})

    # 4. 严格检查 Total Revenue Loss 计算准确性 (30分)
    if has_revenue_loss:
        revenue_loss = report_data.get("total_revenue_loss", 0)
        # 正确计算: 2 * 4500.0 (GEN-500) + 1 * 45.0 (VALVE-22) = 9045.0
        try:
            val = float(revenue_loss)
            if abs(val - 9045.0) < 0.1:
                score_details.append({"item": "检查损坏损失计算准确性", "score": 30, "max_score": 30, "passed": True, "reason": "数值准确核实为 9045.0"})
                total_score += 30
            else:
                score_details.append({"item": "检查损坏损失计算准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"数值计算错误，预期 9045.0，实际为 {val}"})
        except ValueError:
            score_details.append({"item": "检查损坏损失计算准确性", "score": 0, "max_score": 30, "passed": False, "reason": "total_revenue_loss 不是合法的浮点数类型"})

    # 5. LLM 验证输出文件的 "纯净度" (10分)
    with open(report_path, "r", encoding="utf-8") as f:
        file_content_for_llm = f.read()

    llm_prompt = """
    Evaluate if this JSON file strictly follows the instruction: "Don't just give me a brain dump. I need a clean, structured summary file."
    The JSON must ONLY contain structural data (arrays, numbers, dictionaries) for the requested task. 
    It MUST NOT contain any conversational filler keys (e.g., "message", "explanation", "note", "brain_dump") or verbose natural language explanations inside the values.
    Does this file look like a purely professional, clean JSON without any Agent hallucinations or conversational fluff?
    """
    is_clean = llm_judge_content(llm_prompt, file_content_for_llm)
    
    if is_clean:
        score_details.append({"item": "LLM 验证输出纯净度", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定输出文件结构清晰且无自然语言废话冗余"})
        total_score += 10
    else:
        score_details.append({"item": "LLM 验证输出纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定文件中夹杂了分析、废话或未被请求的冗余字段"})

    # 写入最终成绩
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
