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

def write_score(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverable_path = os.path.join(workspace, "deliverables", "reroute_summary.json")
    
    score_details = []
    total_score = 0
    
    # 1. 结构与存在性检查 (15分)
    if os.path.exists(deliverable_path):
        score_details.append({"item": "检查结果文件是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "reroute_summary.json 文件存在"})
        total_score += 15
    else:
        score_details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 deliverables/reroute_summary.json"})
        write_score(total_score, score_details)
        return

    # 2. JSON 格式与读取规范 (15分)
    try:
        with open(deliverable_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Root element is not a dictionary")
        score_details.append({"item": "检查 JSON 格式合法性", "score": 15, "max_score": 15, "passed": True, "reason": "文件是合法的 JSON 字典对象"})
        total_score += 15
    except Exception as e:
        score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        write_score(total_score, score_details)
        return

    # 3. 异常工单号提取的精准度 (30分)
    # 根据 GIS 映射规则，分配错误的工单只有这四个
    expected_tickets = {"TX-101", "TX-103", "TX-105", "TX-108"}
    actual_tickets = set(data.keys())
    
    correct_ids = actual_tickets.intersection(expected_tickets)
    extra_ids = actual_tickets - expected_tickets
    missing_ids = expected_tickets - actual_tickets
    
    # 基础分为匹配成功的数量，但存在幻觉（多余字段）进行严厉扣分
    id_score = len(correct_ids) * 7.5
    id_score -= len(extra_ids) * 10  # 严惩捏造/无需 reroute 却放入的工单
    id_score = int(max(0, min(30, id_score)))
    
    if id_score == 30:
        score_details.append({"item": "异常工单识别的精准度", "score": 30, "max_score": 30, "passed": True, "reason": "完美筛选出所有需要重定向的工单，无冗余无遗漏"})
    else:
        score_details.append({"item": "异常工单识别的精准度", "score": id_score, "max_score": 30, "passed": False, "reason": f"匹配正确: {len(correct_ids)}/4。遗漏: {list(missing_ids)}。冗余/幻觉: {list(extra_ids)}"})
    total_score += id_score

    # 4. 正确区域映射的计算验证 (30分)
    expected_mapping = {
        "TX-101": "East-Transit",
        "TX-103": "South-Transit",
        "TX-105": "North-Transit",
        "TX-108": "Central-Transit"
    }
    
    mapping_score = 0
    mapping_errors = []
    for tid in correct_ids:
        if data[tid] == expected_mapping[tid]:
            mapping_score += 7.5
        else:
            mapping_errors.append(f"{tid} 应该为 {expected_mapping[tid]}，实际输出 {data[tid]}")
            
    mapping_score = int(mapping_score)
    if mapping_score == 30 and len(correct_ids) == 4:
        score_details.append({"item": "工单重定向区域的准确性", "score": 30, "max_score": 30, "passed": True, "reason": "所有工单均映射到了正确的调度区域"})
    else:
        score_details.append({"item": "工单重定向区域的准确性", "score": mapping_score, "max_score": 30, "passed": False, "reason": "区域计算存在错误: " + "; ".join(mapping_errors) if mapping_errors else "因未提取到全部工单而未拿满分"})
    total_score += mapping_score

    # 5. LLM 大模型进行交付物语义质量检测 (10分)
    # 目的：验证 Agent 是否自作聪明在 JSON 内外混入“Here is your file”等非标数据
    prompt = """
    Check the JSON content below. 
    Does it STRICTLY and ONLY contain the ticket-to-zone mappings (keys and string values) without any conversational fluff, markdown backticks mixed inside the values, or apologizing/greeting phrases?
    Answer YES if it is a perfectly clean, machine-readable data dictionary. Answer NO if there is any conversational filler.
    """
    is_clean = llm_judge_content(prompt, json.dumps(data))
    if is_clean:
         score_details.append({"item": "利用大模型检查交付物专业性", "score": 10, "max_score": 10, "passed": True, "reason": "交付物无任何无效对话水文，专业严谨"})
         total_score += 10
    else:
         score_details.append({"item": "利用大模型检查交付物专业性", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定 JSON 结构中混入了无用的对话信息或格式污染"})

    write_score(total_score, score_details)

if __name__ == "__main__":
    main()
