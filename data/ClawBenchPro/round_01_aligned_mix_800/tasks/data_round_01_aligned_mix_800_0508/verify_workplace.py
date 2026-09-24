import os
import sys
import json
import csv
import httpx
from datetime import datetime
from openai import OpenAI

# =====================================================================
# 强制 API 规范：LLM 客户端初始化
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
    """用于检测非结构化文本的统一接口"""
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
# 核心验证逻辑
# =====================================================================
def generate_ground_truth(workspace):
    """通过原生代码执行确定性解析，生成真实的违规 claim_id 集合"""
    policies_dir = os.path.join(workspace, "legacy_records", "policies_dump")
    claims_dir = os.path.join(workspace, "legacy_records", "extracted_claims")
    
    policies = {}
    truth_invalid_claims = set()
    
    # 1. 严格解析 Policy (仅处理 .csv 和 .json)
    if os.path.exists(policies_dir):
        for root, _, files in os.walk(policies_dir):
            for file in files:
                path = os.path.join(root, file)
                try:
                    if file.endswith(".csv"):
                        with open(path, "r", encoding="utf-8") as f:
                            reader = csv.DictReader(f)
                            for row in reader:
                                policies[row["policy_id"]] = row
                    elif file.endswith(".json"):
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            policies[data["policy_id"]] = data
                except Exception:
                    pass # 忽略解析错误的脏文件，模拟真实环境健壮性

    # 2. 严格解析 Claims 并应用业务规则
    if os.path.exists(claims_dir):
        for root, _, files in os.walk(claims_dir):
            for file in files:
                if file.endswith(".json"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            claim = json.load(f)
                        
                        # 规则 0: 忽略 WITHDRAWN
                        if claim.get("claim_status") == "WITHDRAWN":
                            continue
                            
                        cid = claim.get("claim_id")
                        if not cid: continue
                        
                        pref = claim.get("policy_reference")
                        
                        # 规则 1: 找不到保单 -> 违规
                        if pref not in policies:
                            truth_invalid_claims.add(cid)
                            continue
                            
                        pol = policies[pref]
                        
                        # 规则 2: 保单状态不是 ACTIVE -> 违规
                        if pol.get("status") != "ACTIVE":
                            truth_invalid_claims.add(cid)
                            continue
                            
                        # 规则 3: 理赔金额超过限额 -> 违规
                        amount_str = str(claim.get("amount", "0")).replace("$", "").replace(",", "")
                        amount = float(amount_str)
                        limit = float(pol.get("limit", 0))
                        if amount > limit:
                            truth_invalid_claims.add(cid)
                            continue
                            
                        # 规则 4: 理赔日期早于保单生效日期 -> 违规
                        loss_date = datetime.strptime(claim.get("date_of_loss"), "%Y-%m-%d")
                        active_date = datetime.strptime(pol.get("active_date"), "%Y-%m-%d")
                        if loss_date < active_date:
                            truth_invalid_claims.add(cid)
                            continue
                            
                    except Exception:
                        pass # 容错
                        
    return truth_invalid_claims

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "deliverables", "suspicious_claims.json")
    
    details = []
    total_score = 0
    
    # 获取 Ground Truth
    truth_set = generate_ground_truth(workspace)
    
    # ---------------------------------------------------------
    # 验证项 1: 结果文件是否存在 (10分)
    # ---------------------------------------------------------
    file_exists = os.path.exists(target_file)
    if file_exists:
        details.append({"item": "检查 deliverables/suspicious_claims.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "结果文件存在"})
        total_score += 10
    else:
        details.append({"item": "检查 deliverables/suspicious_claims.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "结果文件未找到"})
        # 写入0分记录并直接退出，后续无验证意义
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # ---------------------------------------------------------
    # 验证项 2: 文件格式是否为合法 JSON 且结构正确 (10分) + LLM 容错检测
    # ---------------------------------------------------------
    agent_set = set()
    is_valid_json = False
    
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
            data = json.loads(raw_content)
            if isinstance(data, list) and all(isinstance(x, str) for x in data):
                agent_set = set(data)
                is_valid_json = True
                details.append({"item": "检查 JSON Schema 合法性", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析为纯字符串数组"})
                total_score += 10
            else:
                details.append({"item": "检查 JSON Schema 合法性", "score": 0, "max_score": 10, "passed": False, "reason": "JSON根节点必须是字符串数组，发现捏造的结构或多余字段"})
    except Exception as e:
        # JSON 格式错误时，动用 LLM 判断是否是被 Markdown 语法包裹的非结构化废话
        prompt = "Does this file content essentially provide a list of claim IDs (like 'CLM-XXXXX') despite having markdown formatting or conversational text? Answer YES if the core data is present, NO if it's completely irrelevant or empty."
        llm_judged = llm_judge_content(prompt, raw_content[:2000])
        
        if llm_judged:
            details.append({"item": "检查 JSON Schema 合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"文件不是合法JSON。LLM识别到包含了理赔ID，但由于格式错误扣除格式分。解析错误: {e}"})
        else:
            details.append({"item": "检查 JSON Schema 合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败且LLM判定不包含有效理赔列表。错误: {e}"})

    # ---------------------------------------------------------
    # 验证项 3 & 4: 召回率 (40分) 与 精确率 (40分)
    # 严禁模糊匹配，使用严格的 Set 计算
    # ---------------------------------------------------------
    if is_valid_json and len(truth_set) > 0:
        true_positives = agent_set.intersection(truth_set)
        false_positives = agent_set - truth_set
        
        # 召回率 (Recall) - 满分 40
        recall_ratio = len(true_positives) / len(truth_set)
        recall_score = round(40 * recall_ratio)
        total_score += recall_score
        details.append({
            "item": "验证违规理赔单识别完整度 (Recall)", 
            "score": recall_score, 
            "max_score": 40, 
            "passed": recall_score == 40, 
            "reason": f"应找出 {len(truth_set)} 个违规记录，实际正确找出了 {len(true_positives)} 个。"
        })
        
        # 精确率 (Precision) - 满分 40
        if len(agent_set) > 0:
            precision_ratio = 1.0 - (len(false_positives) / len(agent_set))
        else:
            precision_ratio = 0.0
        precision_score = round(40 * precision_ratio)
        total_score += precision_score
        
        if false_positives:
            reason = f"Agent 错误地包含了 {len(false_positives)} 个合法或 WITHDRAWN 的记录 (False Positives)，扣除相应分数。"
        else:
            reason = "没有误判任何合法的理赔单，精确度完美。"
            
        details.append({
            "item": "验证数据的准确性与幻觉剔除 (Precision)", 
            "score": precision_score, 
            "max_score": 40, 
            "passed": precision_score == 40, 
            "reason": reason
        })
    elif not is_valid_json:
        details.append({"item": "数据逻辑正确性", "score": 0, "max_score": 80, "passed": False, "reason": "由于文件未能被代码成功解析为纯净 JSON 数组，无法进行确定性数据比对，得分为0。"})

    # 输出最终评分
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
