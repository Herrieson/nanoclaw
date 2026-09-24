import os
import sys
import json
import random
import httpx
from datetime import datetime, timedelta
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """
    非结构化文本的统一 LLM 检测接口。
    （本题结果主要是结构化数据，但在发现异常键值对如包含解释性文字时调用防作弊）
    """
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

def calculate_ground_truth():
    """
    使用与环境生成相同的随机数种子和逻辑，算出绝对正确的标准答案。
    """
    random.seed(42)
    
    platforms = {
        "TikTok": 1.5,
        "Instagram": 1.2,
        "X_Twitter": 1.0,
        "Meta_VR": 2.5,
        "Underground_BBS": 0.8
    }
    
    valid_influencers = {}
    for i in range(1, 151):
        handle = f"@user_{random.randint(1000, 9999)}_x"
        base_rate = random.choice([100, 150, 200, 250, 300, 500])
        is_signed = random.choice([True, False, True])
        is_cleared = random.choice([True, False])
        status = "SIGNED" if is_signed else random.choice(["DRAFT", "EXPIRED", "TERMINATED"])
        
        if status == "SIGNED" and is_cleared:
            valid_influencers[handle] = base_rate
            
    valid_handles = list(valid_influencers.keys())
    invalid_handles = [f"@intruder_{random.randint(1000,9999)}_z" for _ in range(80)]
    all_handles_pool = valid_handles + invalid_handles

    total_spend = 0.0
    intruders = set()
    
    start_date = datetime(2024, 1, 1)
    for day_offset in range(30):
        # Format 1: CSV
        csv_platform = random.choice(list(platforms.keys()))
        for _ in range(random.randint(10, 25)):
            h = random.choice(all_handles_pool)
            status = random.choice(["published", "published", "draft", "rejected"])
            qty = random.randint(1, 5)
            
            if h not in valid_influencers:
                intruders.add(h)
            if h in valid_influencers and status == "published":
                total_spend += valid_influencers[h] * qty * platforms[csv_platform]
                
        # Format 2: JSON
        json_platform = random.choice(list(platforms.keys()))
        for _ in range(random.randint(10, 25)):
            h = random.choice(all_handles_pool)
            status = random.choice(["published", "published", "draft", "rejected"])
            qty = random.randint(1, 5)
            
            if h not in valid_influencers:
                intruders.add(h)
            if h in valid_influencers and status == "published":
                total_spend += valid_influencers[h] * qty * platforms[json_platform]
                
        # Format 3: TXT
        txt_platform = random.choice(list(platforms.keys()))
        for _ in range(random.randint(10, 25)):
            h = random.choice(all_handles_pool)
            status = random.choice(["published", "published", "draft", "rejected"])
            qty = random.randint(1, 5)
            
            if h not in valid_influencers:
                intruders.add(h)
            if h in valid_influencers and status == "published":
                total_spend += valid_influencers[h] * qty * platforms[txt_platform]

    return sorted(list(intruders)), round(total_spend, 2)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    audit_dir = os.path.join(workspace, "agency_audit")
    report_file = os.path.join(audit_dir, "final_report.json")
    
    results = []
    total_score = 0
    
    # 获取 Ground Truth
    gt_intruders, gt_spend = calculate_ground_truth()

    # --- 1. 验证目标目录是否存在 (10 分) ---
    if os.path.isdir(audit_dir):
        results.append({"item": "检查目标目录 agency_audit 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        results.append({"item": "检查目标目录 agency_audit 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 agency_audit 目录"})
        
    # --- 2. 验证报告文件是否存在及合法格式 (20 分) ---
    report_data = None
    if os.path.isfile(report_file):
        try:
            with open(report_file, "r") as f:
                report_data = json.load(f)
            results.append({"item": "检查报告文件 final_report.json 是否存在且格式合法", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 文件存在且可解析"})
            total_score += 20
        except json.JSONDecodeError:
            results.append({"item": "检查报告文件 final_report.json 是否存在且格式合法", "score": 0, "max_score": 20, "passed": False, "reason": "文件并非合法的 JSON 格式"})
    else:
        results.append({"item": "检查报告文件 final_report.json 是否存在且格式合法", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 final_report.json 文件"})
        
    # --- 3. 验证 JSON Schema 并防止幻觉生成 (10 分) ---
    if report_data is not None:
        expected_keys = {"unauthorized_intruders", "total_approved_spend"}
        actual_keys = set(report_data.keys())
        
        if actual_keys == expected_keys:
            results.append({"item": "检查返回结果的字段是否有且仅有两个指定键", "score": 10, "max_score": 10, "passed": True, "reason": "仅包含规定的键名"})
            total_score += 10
        else:
            # 如有非结构化冗余字段，调用大模型判定是否为解释性作弊文本
            extra_keys = actual_keys - expected_keys
            if extra_keys:
                extra_content = str({k: report_data[k] for k in extra_keys})
                is_cheat = llm_judge_content("Does the following content look like an AI-generated explanation, hallucinated extra metadata, or a cheating message rather than strict data payload?", extra_content)
                reason = "发现多余字段。大模型判定为作弊/幻觉内容！" if is_cheat else "包含多余的未规定字段。"
                results.append({"item": "检查返回结果的字段是否有且仅有两个指定键", "score": 0, "max_score": 10, "passed": False, "reason": reason})
            else:
                results.append({"item": "检查返回结果的字段是否有且仅有两个指定键", "score": 0, "max_score": 10, "passed": False, "reason": "缺失了必要的结构化字段"})

    # --- 4. 验证入侵者列表 (30 分) ---
    if report_data and "unauthorized_intruders" in report_data:
        agent_intruders = report_data["unauthorized_intruders"]
        if isinstance(agent_intruders, list) and agent_intruders == gt_intruders:
            results.append({"item": "核对非法入侵者名单准确性及排序", "score": 30, "max_score": 30, "passed": True, "reason": "入侵者列表完全一致并按字母排序"})
            total_score += 30
        else:
            diff_len = abs(len(agent_intruders) - len(gt_intruders)) if isinstance(agent_intruders, list) else -1
            results.append({"item": "核对非法入侵者名单准确性及排序", "score": 0, "max_score": 30, "passed": False, "reason": f"入侵者名单不一致，长度误差/排序错误/数据类型错误。误差数量: {diff_len}"})
    else:
        results.append({"item": "核对非法入侵者名单准确性及排序", "score": 0, "max_score": 30, "passed": False, "reason": "未找到 unauthorized_intruders 字段"})

    # --- 5. 验证审批金额计算准确性 (30 分) ---
    if report_data and "total_approved_spend" in report_data:
        try:
            agent_spend = float(report_data["total_approved_spend"])
            if abs(agent_spend - gt_spend) < 0.01:
                results.append({"item": "核对批准的总金额是否精准无误", "score": 30, "max_score": 30, "passed": True, "reason": f"总金额计算精确正确: {gt_spend}"})
                total_score += 30
            else:
                results.append({"item": "核对批准的总金额是否精准无误", "score": 0, "max_score": 30, "passed": False, "reason": f"总金额计算错误。预期: {gt_spend}, 实际: {agent_spend}"})
        except (ValueError, TypeError):
            results.append({"item": "核对批准的总金额是否精准无误", "score": 0, "max_score": 30, "passed": False, "reason": "金额字段的值无法被转化为有效数字"})
    else:
        results.append({"item": "核对批准的总金额是否精准无误", "score": 0, "max_score": 30, "passed": False, "reason": "未找到 total_approved_spend 字段"})

    # --- 输出评分结果 ---
    final_output = {
        "total_score": total_score,
        "details": results
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
if __name__ == "__main__":
    main()
