import os
import sys
import json
import yaml
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

def get_ground_truth(workspace):
    base_dir = os.path.join(workspace, "case_archives")
    records_by_id = {}
    
    pattern = re.compile(r"^(DEPRECATED_)?(CS_\d+)_T\d+_V(\d+)\.(json|txt|yaml|log)$")
    
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            m = pattern.match(f)
            if not m:
                continue
            is_deprecated = m.group(1) is not None
            case_id = m.group(2)
            version = int(m.group(3))
            ext = m.group(4)
            
            if is_deprecated:
                continue
                
            path = os.path.join(root, f)
            
            try:
                if ext == "json":
                    with open(path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                elif ext == "yaml":
                    with open(path, 'r', encoding='utf-8') as file:
                        data = yaml.safe_load(file)
                elif ext == "log":
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        id_m = re.search(r"ID:(CS_\d+)", content)
                        fam_m = re.search(r"FAM:([^ |]+)", content)
                        score_m = re.search(r"SCORE:(\d+)", content)
                        date_m = re.search(r"DATE:([\d-]+)", content)
                        msg_m = re.search(r"MSG:(.*?) \| ENTRY_END", content)
                        data = {
                            "id": id_m.group(1),
                            "family": fam_m.group(1),
                            "score": int(score_m.group(1)),
                            "date": date_m.group(1),
                            "notes": msg_m.group(1).strip()
                        }
                else: # txt
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        id_m = re.search(r"Record for (CS_\d+)", content)
                        fam_m = re.search(r"Family: (.+)", content)
                        score_m = re.search(r"Score: (\d+)", content)
                        date_m = re.search(r"Date: ([\d-]+)", content)
                        notes_m = re.search(r"Notes: (.+)", content)
                        data = {
                            "id": id_m.group(1),
                            "family": fam_m.group(1).strip(),
                            "score": int(score_m.group(1)),
                            "date": date_m.group(1).strip(),
                            "notes": notes_m.group(1).strip()
                        }
            except Exception as e:
                continue
                
            if case_id not in records_by_id or version > records_by_id[case_id]['version']:
                data['version'] = version
                records_by_id[case_id] = data

    invalid_date_count = 0
    high_risk_ids = set()
    
    for cid, data in records_by_id.items():
        try:
            year = int(data['date'].split('-')[0])
            if year >= 2025:
                invalid_date_count += 1
            else:
                score = int(data['score'])
                notes = data['notes']
                if score < 40 and ("Housing Instability" in notes or "Child Safety" in notes):
                    high_risk_ids.add(cid)
        except Exception:
            continue
            
    return invalid_date_count, high_risk_ids

def extract_all_values(obj):
    values = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            values.extend(extract_all_values(v))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(extract_all_values(item))
    else:
        values.append(obj)
    return values

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # 动态计算 Ground Truth
    gt_invalid_count, gt_high_risk_ids = get_ground_truth(workspace)
    
    target_file = os.path.join(workspace, "audit_report", "high_risk_summary.json")
    
    details = []
    total_score = 0
    
    # 1. 检查目标文件是否存在 (10 分)
    if os.path.exists(target_file):
        total_score += 10
        details.append({"item": "检查目标文件 audit_report/high_risk_summary.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    else:
        details.append({"item": "检查目标文件 audit_report/high_risk_summary.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2)
        return

    # 2. 检查 JSON 格式是否合法 (10 分)
    agent_data = None
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
            agent_data = json.loads(raw_content)
        total_score += 10
        details.append({"item": "检查输出是否为合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式合法"})
    except Exception as e:
        details.append({"item": "检查输出是否为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 提取 JSON 中的所有标量值
    all_values = extract_all_values(agent_data)
    
    # 3. 检查无效日期统计总数 (30 分)
    if gt_invalid_count in all_values or str(gt_invalid_count) in all_values:
        total_score += 30
        details.append({"item": "检查无效日期记录总数是否正确", "score": 30, "max_score": 30, "passed": True, "reason": f"找到正确的无效记录数: {gt_invalid_count}"})
    else:
        details.append({"item": "检查无效日期记录总数是否正确", "score": 0, "max_score": 30, "passed": False, "reason": f"未找到正确的无效记录数，预期为 {gt_invalid_count}"})

    # 4. 检查高风险名单是否精准匹配 (40 分)
    # 提取 JSON 里面所有看起来像 ID 的字符串
    agent_ids = set()
    for val in all_values:
        if isinstance(val, str) and val.startswith("CS_") and len(val) >= 6:
            agent_ids.add(val)
            
    if not agent_ids:
        details.append({"item": "检查高风险家庭名单", "score": 0, "max_score": 40, "passed": False, "reason": "未在 JSON 中提取到任何 CS_ 开头的 ID"})
    else:
        extra_ids = agent_ids - gt_high_risk_ids
        missing_ids = gt_high_risk_ids - agent_ids
        
        if not extra_ids and not missing_ids:
            total_score += 40
            details.append({"item": "检查高风险家庭名单", "score": 40, "max_score": 40, "passed": True, "reason": "高风险 ID 完全匹配，无遗漏无多余"})
        else:
            partial_score = 0
            reason_str = "高风险名单不完美: "
            if missing_ids:
                reason_str += f"遗漏 {len(missing_ids)} 个; "
            if extra_ids:
                reason_str += f"多出 {len(extra_ids)} 个错误数据; "
                # 严惩幻觉或未正确过滤废弃版本的数据
                partial_score = max(0, 10 - len(extra_ids)*5) 
            else:
                # 没多但少了
                partial_score = max(0, 40 - len(missing_ids)*10)
            
            total_score += partial_score
            details.append({"item": "检查高风险家庭名单", "score": partial_score, "max_score": 40, "passed": False, "reason": reason_str})

    # 5. LLM 语义校验 - 检查平均得分等信息的语义描述 (10 分)
    llm_prompt = "Does this JSON output explicitly mention or structure the 'average score' (or 'avg_score', 'mean score') of the high-risk families, and clearly distinguish it from the invalid date records count? Only answer YES if both elements are semantically clear."
    is_semantic_clear = llm_judge_content(llm_prompt, raw_content)
    if is_semantic_clear:
        total_score += 10
        details.append({"item": "利用大模型校验数据结构的语义完备性", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定 JSON 结构中关于平均分及无效记录的语义描述清晰"})
    else:
        details.append({"item": "利用大模型校验数据结构的语义完备性", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定 JSON 中未能清晰呈现平均得分或缺乏明确的上下文结构说明"})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
