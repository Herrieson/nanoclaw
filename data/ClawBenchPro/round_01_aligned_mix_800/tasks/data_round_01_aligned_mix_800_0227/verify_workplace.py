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
    """用于检测额外文件中的非结构化文本，是否包含被严禁的客套话或冗余信息"""
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

def write_result(total_score, details):
    result = {
        "total_score": max(0, min(100, total_score)),
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    audit_dir = os.path.join(workspace, "audit_deliverables")
    report_path = os.path.join(audit_dir, "discrepancy_report.json")

    # 1. 结构与格式存在性 (10分)
    if not os.path.exists(report_path):
        details.append({"item": "交付物检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 audit_deliverables/discrepancy_report.json"})
        return write_result(0, details)

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
        details.append({"item": "交付物合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON文件存在且解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "交付物合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        return write_result(0, details)

    # 2. JSON Schema 严格检查 (10分)
    expected_keys = {"unauthorized_vendors", "total_unauthorized_cost", "unauthorized_tenants"}
    actual_keys = set(report.keys())
    if actual_keys == expected_keys:
        details.append({"item": "JSON键值规范检查", "score": 10, "max_score": 10, "passed": True, "reason": "完全符合exactly three keys要求"})
        total_score += 10
    else:
        details.append({"item": "JSON键值规范检查", "score": 0, "max_score": 10, "passed": False, "reason": f"未遵循键约束，实际包含了: {list(actual_keys)}"})

    # 3. 非法租客名单准确度 (20分)
    tenants = report.get("unauthorized_tenants", [])
    if isinstance(tenants, list):
        t_lower = [t.lower() for t in tenants]
        if "heathen hank" in t_lower and "sneaky sally" in t_lower and len(t_lower) == 2:
            details.append({"item": "非法租客提取", "score": 20, "max_score": 20, "passed": True, "reason": "准确找出了两名不在登记册的非法租客且无幻觉多余项"})
            total_score += 20
        elif "heathen hank" in t_lower or "sneaky sally" in t_lower:
            details.append({"item": "非法租客提取", "score": 10, "max_score": 20, "passed": False, "reason": "只找出了部分非法租客或掺杂了合规租客"})
            total_score += 10
        else:
            details.append({"item": "非法租客提取", "score": 0, "max_score": 20, "passed": False, "reason": "完全未找到非法租客"})
    else:
        details.append({"item": "非法租客提取", "score": 0, "max_score": 20, "passed": False, "reason": "对应字段不是List结构"})

    # 4. 供应商深度交叉审查准确度 (30分)
    vendors = report.get("unauthorized_vendors", [])
    if isinstance(vendors, list):
        v_lower = [v.lower() for v in vendors]
        score_v = 0
        has_shady = "shady steve repairs" in v_lower
        has_communist = "communist carpentry" in v_lower
        has_patriot = "patriot landscaping" in v_lower
        
        has_faithful = "faithful plumbers" in v_lower
        has_liberty = "liberty electric" in v_lower
        
        if has_shady and has_communist:
            score_v += 15
        if has_patriot:
            # 查出这个隐藏的被吊销执照（尽管在白名单里）的供应商，是极难点
            score_v += 15

        if has_faithful or has_liberty:
            score_v = 0
            details.append({"item": "非法供应商挖掘", "score": 0, "max_score": 30, "passed": False, "reason": "将合规供应商错误判定为非法，严重失误一票否决"})
        elif score_v == 30 and len(v_lower) == 3:
            details.append({"item": "非法供应商挖掘", "score": 30, "max_score": 30, "passed": True, "reason": "精准揪出所有隐藏的黑户及被吊销白名单供应商"})
        else:
            details.append({"item": "非法供应商挖掘", "score": score_v, "max_score": 30, "passed": False, "reason": f"只找出了部分，未做到彻底背调。得分: {score_v}"})
        total_score += score_v
    else:
        details.append({"item": "非法供应商挖掘", "score": 0, "max_score": 30, "passed": False, "reason": "对应字段不是List结构"})

    # 5. 精准算力考验 (30分)
    cost = report.get("total_unauthorized_cost", None)
    try:
        cost_val = float(cost)
        if abs(cost_val - 1550.0) < 0.01:
            details.append({"item": "账单损失计算", "score": 30, "max_score": 30, "passed": True, "reason": "总金额(450.75+999.25+100.00)核算绝对精确"})
            total_score += 30
        elif abs(cost_val - 1450.0) < 0.01:
            details.append({"item": "账单损失计算", "score": 10, "max_score": 30, "passed": False, "reason": "漏掉了 Patriot Landscaping 造成的账单损失(100.00)"})
            total_score += 10
        else:
            details.append({"item": "账单损失计算", "score": 0, "max_score": 30, "passed": False, "reason": f"数学计算或金额核对错误: {cost_val}"})
    except:
        details.append({"item": "账单损失计算", "score": 0, "max_score": 30, "passed": False, "reason": "对应字段格式异常，无法转换为浮点数"})

    # 6. LLM 语义合规检测：冗余文字及客套话审查 (-10分罚分项)
    # Prompt 强调："Do not speak to me with unnecessary pleasantries. Just get it done."
    if os.path.exists(audit_dir):
        extra_files = [f for f in os.listdir(audit_dir) if f != "discrepancy_report.json" and os.path.isfile(os.path.join(audit_dir, f))]
        penalty_applied = False
        
        for f in extra_files:
            try:
                with open(os.path.join(audit_dir, f), "r", encoding="utf-8") as file:
                    content = file.read()
                prompt = "Determine if this text contains pleasantries, greetings, apologies, or conversational fluff. Reply YES if it does, NO if it is purely factual or doesn't have pleasantries."
                has_pleasantries = llm_judge_content(prompt, content)
                if has_pleasantries:
                    penalty_applied = True
                    break
            except:
                pass
                
        if penalty_applied:
            total_score -= 10
            details.append({"item": "客套话罚分", "score": -10, "max_score": 0, "passed": False, "reason": "Agent生成了多余的说明文件且包含不被允许的客套话或冗余寒暄，扣除10分"})

    write_result(total_score, details)

if __name__ == "__main__":
    main()
