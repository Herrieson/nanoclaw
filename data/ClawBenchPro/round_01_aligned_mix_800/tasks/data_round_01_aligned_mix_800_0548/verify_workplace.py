import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# =====================================================================
# 强制 API 规范：使用 OpenAI SDK 结合 Mock 参数，必须关闭 SSL 验证
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
    """
    使用大模型检查是否存在幻觉、非结构化的废话、冗余的解释性文本等。
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

# =====================================================================
# 物理计算探针：严格从脏数据中还原 Ground Truth
# =====================================================================
def calculate_ground_truth(workspace):
    gt_cleared_hours = 0.0
    gt_total_exp = 0.0
    
    # 1. 解析 Roster
    roster_path = os.path.join(workspace, "records", "roster", "master_roster.csv")
    names_map = {}
    if os.path.exists(roster_path):
        with open(roster_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                names_map[row['Vol_ID']] = f"{row['First_Name']} {row['Last_Name']}"
                
    # 2. 解析 Compliance Logs
    comp_dir = os.path.join(workspace, "records", "compliance_logs")
    status_map = {}
    if os.path.exists(comp_dir):
        for fname in os.listdir(comp_dir):
            if fname.endswith(".json"):
                with open(os.path.join(comp_dir, fname), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for ev in data.get('events', []):
                        vid = ev['vid']
                        ts = ev['timestamp']
                        st = ev['status']
                        # 仅保留最新时间戳的状态
                        if vid not in status_map or ts > status_map[vid]['timestamp']:
                            status_map[vid] = {'status': st, 'timestamp': ts}
                            
    # 3. 解析 Timesheets 累加工时
    ts_dir = os.path.join(workspace, "records", "timesheets")
    hours_map = {}
    if os.path.exists(ts_dir):
        for root, _, files in os.walk(ts_dir):
            for fname in files:
                if fname.endswith(".csv"):
                    with open(os.path.join(root, fname), 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            vid = row['Vol_ID']
                            h = float(row['Hours_Worked'])
                            hours_map[vid] = hours_map.get(vid, 0.0) + h
                            
    # 4. 解析 Finances 清洗累加金额
    fin_dir = os.path.join(workspace, "finances", "receipts")
    if os.path.exists(fin_dir):
        for root, _, files in os.walk(fin_dir):
            for fname in files:
                if fname.endswith(".csv"):
                    with open(os.path.join(root, fname), 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row['Status'] == 'VERIFIED':
                                raw = row['Amount']
                                raw = raw.replace('$', '').replace('USD', '').replace(',', '').strip()
                                gt_total_exp += float(raw)
                                
    # 5. 整合得出未通过审核人员名单及对应总清算工时
    unvetted = []
    for vid, hrs in hours_map.items():
        if hrs > 0:
            st = status_map.get(vid, {}).get('status', 'UNVETTED')
            if st == 'CLEARED':
                gt_cleared_hours += hrs
            else:
                if vid in names_map:
                    unvetted.append(names_map[vid])
                    
    unvetted = sorted(list(set(unvetted)))
    
    return {
        "cleared_volunteer_hours": gt_cleared_hours,
        "total_verified_expenses": gt_total_exp,
        "unvetted_volunteers_with_hours": unvetted
    }

# =====================================================================
# 验证主逻辑
# =====================================================================
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    
    deliverables_dir = os.path.join(workspace, "deliverables")
    report_file = os.path.join(deliverables_dir, "board_report.json")
    
    # 1. 检查基础环境结构 (10分)
    if os.path.isdir(deliverables_dir):
        results.append({"item": "检查 deliverables 目录是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "目录已创建"})
        total_score += 5
    else:
        results.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "目录未创建"})
        
    if os.path.isfile(report_file):
        results.append({"item": "检查 board_report.json 文件是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件已创建"})
        total_score += 5
    else:
        results.append({"item": "检查 board_report.json 文件是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件缺失"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2)
        return

    # 2. 检查 JSON 语法及严格 Schema (10分)
    with open(report_file, "r", encoding="utf-8") as f:
        file_content = f.read()
    
    try:
        agent_data = json.loads(file_content)
        req_keys = {"cleared_volunteer_hours", "total_verified_expenses", "unvetted_volunteers_with_hours"}
        agent_keys = set(agent_data.keys())
        
        if req_keys.issubset(agent_keys):
            results.append({"item": "检查 JSON Schema合法性及必填键", "score": 10, "max_score": 10, "passed": True, "reason": "完整包含所有必需的数据键"})
            total_score += 10
        else:
            missing = req_keys - agent_keys
            results.append({"item": "检查 JSON Schema合法性及必填键", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失字段: {missing}"})
    except Exception:
        results.append({"item": "检查 JSON Schema合法性及必填键", "score": 0, "max_score": 10, "passed": False, "reason": "无法被原生 JSON 解析，格式严重损坏"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2)
        return

    # 3. LLM 语义检测：检查是否夹带无效废话或违反强硬且简洁的 Persona 要求 (10分)
    llm_prompt = "Examine this text. The user strictly requested a clean, executive-level JSON file. Does this file contain any conversational sentences (e.g. 'Here is your report', 'Sorry, I couldn't process'), apologetic remarks, or any non-JSON textual garbage outside the strict payload? Answer YES if there is any conversational junk/apologies, NO if it is purely JSON."
    has_junk = llm_judge_content(llm_prompt, file_content)
    
    if has_junk:
        results.append({"item": "LLM 检查文件内容纯度与严谨性", "score": 0, "max_score": 10, "passed": False, "reason": "大模型检测出包含非结构化废话或致歉文案，不符合 executive-level 要求"})
    else:
        if agent_keys == req_keys:
            results.append({"item": "LLM 检查文件内容纯度与严谨性", "score": 10, "max_score": 10, "passed": True, "reason": "文件纯净，严格服从 Persona 仅输出确定的 JSON 结构"})
            total_score += 10
        else:
            results.append({"item": "LLM 检查文件内容纯度与严谨性", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 内存在自行捏造的多余 Key，严重违反合规要求"})

    # 计算标准答案以评估数据正确度
    gt = calculate_ground_truth(workspace)
    
    # 4. 验证 Cleared Volunteer Hours (20分)
    try:
        agent_hours = float(agent_data.get("cleared_volunteer_hours", -1))
        if abs(agent_hours - gt["cleared_volunteer_hours"]) < 0.1:
            results.append({"item": "核对 cleared_volunteer_hours 的计算准确度", "score": 20, "max_score": 20, "passed": True, "reason": "有效过滤最新合规状态，工时累加完全准确"})
            total_score += 20
        else:
            results.append({"item": "核对 cleared_volunteer_hours 的计算准确度", "score": 0, "max_score": 20, "passed": False, "reason": f"未按最新 timestamp 进行审核过滤或累加出错. Expected: {gt['cleared_volunteer_hours']}, Got: {agent_hours}"})
    except:
        results.append({"item": "核对 cleared_volunteer_hours 的计算准确度", "score": 0, "max_score": 20, "passed": False, "reason": "非预期的数值类型"})

    # 5. 验证 Total Verified Expenses (20分)
    try:
        agent_exp = float(agent_data.get("total_verified_expenses", -1))
        if abs(agent_exp - gt["total_verified_expenses"]) < 0.1:
            results.append({"item": "核对 total_verified_expenses 清洗准确度", "score": 20, "max_score": 20, "passed": True, "reason": "完美过滤了废土级脏格式数据与非法状态，金额完全准确"})
            total_score += 20
        else:
            results.append({"item": "核对 total_verified_expenses 清洗准确度", "score": 0, "max_score": 20, "passed": False, "reason": f"由于脏数据处理或过滤器缺陷导致计算错误. Expected: {gt['total_verified_expenses']}, Got: {agent_exp}"})
    except:
        results.append({"item": "核对 total_verified_expenses 清洗准确度", "score": 0, "max_score": 20, "passed": False, "reason": "非预期的数值类型"})

    # 6. 验证 Unvetted Volunteers With Hours (30分)
    agent_list = agent_data.get("unvetted_volunteers_with_hours", [])
    if isinstance(agent_list, list) and agent_list == gt["unvetted_volunteers_with_hours"]:
        results.append({"item": "核对 unvetted_volunteers_with_hours 人员与排序", "score": 30, "max_score": 30, "passed": True, "reason": "名单精准匹配，且严格按照 Full Name 字母序排序"})
        total_score += 30
    else:
        results.append({"item": "核对 unvetted_volunteers_with_hours 人员与排序", "score": 0, "max_score": 30, "passed": False, "reason": "人员遗漏、误报或未严格按字典序排序"})

    # 输出得分报告
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2)

if __name__ == "__main__":
    main()
