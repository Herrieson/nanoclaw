import os
import sys
import json
import httpx
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
    """大模型判定文本语义内容的统一接口"""
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

def jaccard_sim(set_a, set_b):
    if not set_a and not set_b:
        return 1.0
    union_len = len(set_a.union(set_b))
    return len(set_a.intersection(set_b)) / union_len if union_len > 0 else 0

def extract_ground_truth(workspace):
    """
    通过原生严格的代码执行还原真实答案，避免幻觉校验。
    """
    registry_dir = os.path.join(workspace, "registry", "fragments")
    authorized_names = set()
    for root, _, files in os.walk(registry_dir):
        for f in files:
            if f.endswith('.json') and 'deprecated' not in f:
                try:
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if data.get("status") == "ACTIVE" and "full_name" in data:
                            authorized_names.add(data.get("full_name"))
                except Exception:
                    pass

    archives_dir = os.path.join(workspace, "archives")
    illegal_volunteers = set()
    total_duration = 0
    anomalous_ids = set()

    for root, _, files in os.walk(archives_dir):
        for f in files:
            if f.endswith('.json'):
                try:
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as fp:
                        content = json.load(fp)
                        logs = content if isinstance(content, list) else [content]
                        for log in logs:
                            if not isinstance(log, dict):
                                continue
                            operator = log.get("operator")
                            bp = log.get("systolic_bp", 0)
                            duration = log.get("duration_min", 0)
                            status = log.get("status", "")
                            entry_id = log.get("entry_id")

                            if operator:
                                if operator not in authorized_names:
                                    illegal_volunteers.add(operator)
                                else:
                                    if status == "COMPLETED":
                                        total_duration += duration
                            
                            if bp > 200 and entry_id:
                                anomalous_ids.add(entry_id)
                except Exception:
                    pass
    
    return authorized_names, illegal_volunteers, total_duration, anomalous_ids

def verify_workplace(workspace):
    details = []
    total_score = 0

    # 1. 计算当前环境中的 Ground Truth
    _, gt_illegal, gt_duration, gt_anomalies = extract_ground_truth(workspace)

    # 2. 检查输出目标文件是否存在
    report_path = os.path.join(workspace, "deliverables", "audit_report.json")
    if not os.path.exists(report_path):
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 deliverables/audit_report.json 不存在"})
        return 0, details
    else:
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件成功生成"})
        total_score += 10

    # 3. 检查 JSON Schema 合法性并加载
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "标准 JSON 格式解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        return total_score, details

    # 4. 深度遍历 JSON 收集所有可能是答案的集合/整数/文本
    all_lists = []
    all_ints = []
    all_strings = []
    
    def traverse(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                traverse(v)
        elif isinstance(obj, list):
            is_str_list = all(isinstance(x, str) for x in obj)
            if is_str_list and len(obj) > 0:
                all_lists.append(set(obj))
            for v in obj:
                traverse(v)
        elif isinstance(obj, int) and not isinstance(obj, bool):
            all_ints.append(obj)
        elif isinstance(obj, str):
            all_strings.append(obj)

    traverse(report_data)

    # 5. 校验非法人员名单 (25分) - 找寻最高匹配度的列表
    best_ill_score = 0
    best_ill_reason = "未找到包含任何匹配非法人员的列表数据"
    for lst in all_lists:
        sim = jaccard_sim(lst, gt_illegal)
        if sim > 0:
            score = int(sim * 25)
            if score > best_ill_score:
                best_ill_score = score
                if score == 25:
                    best_ill_reason = "精确无误地匹配了所有的非法幽灵人员名单"
                else:
                    best_ill_reason = f"模糊匹配到部分人员，包含幻觉或漏网之鱼，相似度 {sim:.2f}"
    details.append({"item": "精准验证：非法人员名单抓取", "score": best_ill_score, "max_score": 25, "passed": best_ill_score == 25, "reason": best_ill_reason})
    total_score += best_ill_score

    # 6. 校验异常血压 ID 名单 (25分)
    best_ano_score = 0
    best_ano_reason = "未找到包含异常血压心脏炸弹记录 ID 的列表数据"
    for lst in all_lists:
        sim = jaccard_sim(lst, gt_anomalies)
        if sim > 0:
            score = int(sim * 25)
            if score > best_ano_score:
                best_ano_score = score
                if score == 25:
                    best_ano_reason = "精确无误地提取了所有的收缩压极高异常日志的 entry_id"
                else:
                    best_ano_reason = f"部分提取或存在多余的错误 ID 数据，相似度 {sim:.2f}"
    details.append({"item": "精准验证：极高血压异常记录定位", "score": best_ano_score, "max_score": 25, "passed": best_ano_score == 25, "reason": best_ano_reason})
    total_score += best_ano_score

    # 7. 校验合法工时总数 (20分)
    dur_score = 0
    dur_reason = f"未找到匹配的工时整数（目标真实时长: {gt_duration}）"
    if gt_duration in all_ints:
        dur_score = 20
        dur_reason = "数学计算与数据清洗完全正确，过滤了冗余状态并得出了正确总时长！"
    details.append({"item": "精准验证：合法志愿者的 COMPLETED 服务工时累加", "score": dur_score, "max_score": 20, "passed": dur_score == 20, "reason": dur_reason})
    total_score += dur_score

    # 8. LLM 柔性探针：检测是否有合适的医疗事故与时间紧迫总结 (10分)
    llm_score = 0
    llm_reason = "未检测到包含医学警告或紧急情绪的文本信息"
    for s in all_strings:
        if len(s) >= 20: # 避免处理过短的常规字符串
            prompt = "Does this text express a sense of warning about dangerous health conditions (like systolic BP > 200), or mention urgency/electricity failure as per a survival log context?"
            is_valid = llm_judge_content(prompt, s)
            if is_valid:
                llm_score = 10
                llm_reason = "通过大模型检测到 Agent 在报告中附加了生动的警告和紧急情绪通报，表现出良好的角色代入"
                break
    details.append({"item": "LLM语义验证：警告与代入感报告总结", "score": llm_score, "max_score": 10, "passed": llm_score == 10, "reason": llm_reason})
    total_score += llm_score

    return total_score, details

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    score, dts = verify_workplace(workspace_path)
    
    result = {
        "total_score": score,
        "details": dts
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Validation complete. Total Score: {score}")
