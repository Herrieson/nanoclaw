import os
import sys
import json
import httpx
from openai import OpenAI

# =====================================================================
# 强制 API 规范：初始化 OpenAI 客户端，关闭 SSL 验证
# =====================================================================
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
    """大模型统一检测接口：用于非结构化文本的语义、幻觉与语调验证"""
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
    deliverable_dir = os.path.join(workspace, "deliverables")
    summary_file = os.path.join(deliverable_dir, "audit_summary.json")
    
    total_score = 0
    details = []

    # ---------------------------------------------------------
    # 检查项 1：目录与文件结构 (15分)
    # ---------------------------------------------------------
    step1_score = 0
    step1_reason = "Deliverables目录或audit_summary.json文件丢失"
    if os.path.isdir(deliverable_dir) and os.path.isfile(summary_file):
        step1_score = 15
        step1_reason = "目录和目标JSON文件均存在"
    details.append({"item": "检查交付目录与文件结构", "score": step1_score, "max_score": 15, "passed": step1_score == 15, "reason": step1_reason})

    # 如果文件不存在，提前结束
    if step1_score == 0:
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=4)
        return

    # ---------------------------------------------------------
    # 检查项 2：JSON Schema与合法性 (15分)
    # ---------------------------------------------------------
    step2_score = 0
    step2_reason = ""
    try:
        with open(summary_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            raw_content = json.dumps(data)
        
        if "delinquent_payers" in data and "solar_candidates" in data:
            step2_score = 15
            step2_reason = "JSON解析成功，且包含指定的关键节点"
        else:
            step2_reason = "JSON解析成功，但缺少 delinquent_payers 或 solar_candidates 节点"
    except Exception as e:
        step2_reason = f"JSON格式错误或解析失败: {e}"
        data = {}

    details.append({"item": "检查JSON格式与必要Schema", "score": step2_score, "max_score": 15, "passed": step2_score == 15, "reason": step2_reason})

    # ---------------------------------------------------------
    # 检查项 3：欠费租户计算逻辑判定 (30分 - 原生代码严格校验)
    # 核心逻辑：T002 (Linda Chen, 实付4000 < 应付4500), T004 (Robert Taylor, 实付3600 < 应付5400)
    # ---------------------------------------------------------
    step3_score = 0
    step3_reason = []
    delinquents = data.get("delinquent_payers", [])
    if isinstance(delinquents, list):
        delinquent_str = " ".join([str(x).lower() for x in delinquents])
        
        # 命中检测
        has_linda = "linda chen" in delinquent_str or ("linda" in delinquent_str and "chen" in delinquent_str)
        has_robert = "robert taylor" in delinquent_str or ("robert" in delinquent_str and "taylor" in delinquent_str)
        
        if has_linda: step3_score += 15
        if has_robert: step3_score += 15
        
        # 严查假阳性 (False Positives) - 扣分机制
        false_positives = [n for n in ["james wilson", "sarah miller", "gina smith"] if n in delinquent_str or n.split()[0] in delinquent_str]
        if false_positives:
            penalty = len(false_positives) * 10
            step3_score = max(0, step3_score - penalty)
            step3_reason.append(f"计算错误，捏造了额外欠费人员 (扣{penalty}分): {false_positives}")
            
        if step3_score == 30:
            step3_reason.append("精准识别并仅输出了真实欠费的租户姓名。")
        elif step3_score > 0 and not false_positives:
            step3_reason.append("部分识别出了欠费租户，但有遗漏。")
    else:
        step3_reason.append("delinquent_payers 节点不是规范的数组格式。")

    details.append({"item": "欠缴租金租户的精准核算", "score": step3_score, "max_score": 30, "passed": step3_score == 30, "reason": "; ".join(step3_reason)})

    # ---------------------------------------------------------
    # 检查项 4：太阳能改造高能耗单元筛选 (30分 - 原生代码严格校验)
    # 核心逻辑：A2, B2, C1 符合条件
    # ---------------------------------------------------------
    step4_score = 0
    step4_reason = []
    candidates = data.get("solar_candidates", [])
    if isinstance(candidates, list):
        candidates_str = [str(x).upper() for x in candidates]
        
        for target in ["A2", "B2", "C1"]:
            if any(target in x for x in candidates_str):
                step4_score += 10
                
        # 假阳性严防：A1 和 B1 不属于 High-Energy
        false_positives_solar = [n for n in ["A1", "B1"] if any(n in x for x in candidates_str)]
        if false_positives_solar:
            penalty = len(false_positives_solar) * 15 # 每个假阳性严重扣分
            step4_score = max(0, step4_score - penalty)
            step4_reason.append(f"参数提取错误，错误包含了不合格单元: {false_positives_solar}")
            
        if step4_score == 30:
            step4_reason.append("完全准确地找出了所有高能耗太阳能改造候选单元。")
    else:
        step4_reason.append("solar_candidates 节点不是规范的数组格式。")

    details.append({"item": "高能耗候选单元的科学筛选", "score": step4_score, "max_score": 30, "passed": step4_score == 30, "reason": "; ".join(step4_reason)})

    # ---------------------------------------------------------
    # 检查项 5：LLM 语义与防幻觉核查 (10分)
    # ---------------------------------------------------------
    prompt_text = (
        "Check the following JSON output from an AI Agent. "
        "The agent was asked to provide a strict data summary of delinquent payers and solar candidates. "
        "Examine the JSON string. Does it strictly contain factual data WITHOUT any fabricated personal excuses "
        "(e.g., hallucinating that someone 'lost their job' or 'had medical issues') or excessive unprofessional chat? "
        "Return YES if it is clean, factual, and professional. Return NO if it hallucinates reasons not supported by standard audit data."
    )
    llm_passed = llm_judge_content(prompt_text, raw_content if 'raw_content' in locals() else "")
    
    step5_score = 10 if llm_passed else 0
    step5_reason = "JSON结果整洁且无编造背景故事的幻觉。" if llm_passed else "大模型检测出Agent捏造了未经证实的附加信息或语气不符合商业审查规范。"
    details.append({"item": "利用大模型检查内容专业性与防幻觉", "score": step5_score, "max_score": 10, "passed": llm_passed, "reason": step5_reason})

    # =====================================================================
    # 综合计分与落盘
    # =====================================================================
    total_score = step1_score + step2_score + step3_score + step4_score + step5_score
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
