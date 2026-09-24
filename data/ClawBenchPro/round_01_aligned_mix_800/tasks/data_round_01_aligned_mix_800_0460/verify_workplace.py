import os
import sys
import json
import csv
import httpx
from openai import OpenAI
import traceback

# ---------------------------------------------------------
# LLM Configuration (Mandatory as per Architectural Rules)
# ---------------------------------------------------------
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
    LLM API for non-structural text validation. 
    Strictly forces yes/no boolean output.
    """
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[Content to Evaluate]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

# ---------------------------------------------------------
# Ground Truth Computation (Dynamic & Deterministic)
# ---------------------------------------------------------
def compute_ground_truth(workspace):
    """
    Simulates the exact deterministic logic to get the absolute ground truth
    without relying on static hardcoding, preventing random seed issues.
    """
    patients = set()
    total_hours = 0.0
    
    registry = {}
    registry_dir = os.path.join(workspace, "patient_registry")
    if os.path.exists(registry_dir):
        for f in os.listdir(registry_dir):
            if f.endswith(".json"):
                path = os.path.join(registry_dir, f)
                try:
                    with open(path, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                        if "patient_id" in data and "program" in data:
                            registry[data["patient_id"]] = data["program"]
                except:
                    pass

    logs_dir = os.path.join(workspace, "daily_logs")
    if os.path.exists(logs_dir):
        # Only Nov 01 to Nov 15
        for day in range(1, 16):
            date_str = f"2023-11-{day:02d}"
            day_dir = os.path.join(logs_dir, date_str)
            if not os.path.exists(day_dir):
                continue
                
            # A. CSV
            for c in range(3):
                csv_path = os.path.join(day_dir, f"log_{c}.csv")
                if os.path.exists(csv_path):
                    try:
                        with open(csv_path, "r", encoding="utf-8") as fp:
                            reader = csv.DictReader(fp)
                            for row in reader:
                                if row.get("doctor_name") == "Aris" and row.get("status") == "finalized":
                                    pid = row.get("patient_id")
                                    if registry.get(pid) == "Charity":
                                        patients.add(pid)
                                        val = float(row.get("time", 0))
                                        if row.get("unit") in ["mins", "minutes", "m"]:
                                            val /= 60.0
                                        total_hours += val
                    except:
                        pass
                        
            # B. JSON
            for j in range(2):
                json_path = os.path.join(day_dir, f"records_{j}.json")
                if os.path.exists(json_path):
                    try:
                        with open(json_path, "r", encoding="utf-8") as fp:
                            data = json.load(fp)
                            for item in data:
                                if item.get("doc") == "Aris" and item.get("is_draft") is False:
                                    pid = item.get("uid")
                                    if registry.get(pid) == "Charity":
                                        patients.add(pid)
                                        val = float(item.get("duration", 0))
                                        if item.get("unit") in ["mins", "minutes", "m"]:
                                            val /= 60.0
                                        total_hours += val
                    except:
                        pass
                        
            # C. TXT
            txt_path = os.path.join(day_dir, "scribbles.txt")
            if os.path.exists(txt_path):
                try:
                    with open(txt_path, "r", encoding="utf-8") as fp:
                        for line in fp:
                            line = line.strip()
                            if not line: continue
                            parts = [p.strip() for p in line.split("|")]
                            if len(parts) == 4:
                                status = parts[0]
                                pid_part = parts[1]
                                time_part = parts[2]
                                doc_part = parts[3]
                                
                                doc = doc_part.replace("Doc:", "").strip()
                                if doc == "Aris" and status == "[FINAL]":
                                    pid = pid_part.replace("ID:", "").strip()
                                    if registry.get(pid) == "Charity":
                                        patients.add(pid)
                                        t_str = time_part.replace("Time:", "").strip()
                                        t_val_str, unit = t_str.split()
                                        val = float(t_val_str)
                                        if unit in ["mins", "minutes", "m"]:
                                            val /= 60.0
                                        total_hours += val
                except:
                    pass
                                
    return sorted(list(patients)), round(total_hours, 2)

# ---------------------------------------------------------
# Evaluation Logic
# ---------------------------------------------------------
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    gt_patients, gt_hours = compute_ground_truth(workspace)
    details = []
    total_score = 0
    
    # 1. Directory Check (10 pts)
    admin_dir = os.path.join(workspace, "admin_delivery")
    if os.path.exists(admin_dir) and os.path.isdir(admin_dir):
        details.append({"item": "检查目标输出目录是否创建", "score": 10, "max_score": 10, "passed": True, "reason": "admin_delivery/ 目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标输出目录是否创建", "score": 0, "max_score": 10, "passed": False, "reason": "admin_delivery/ 目录不存在"})
        
    # 2. JSON Integrity Check (20 pts)
    report_path = os.path.join(admin_dir, "charity_report.json")
    agent_data = None
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                agent_data = json.load(f)
            details.append({"item": "JSON报告合法性校验", "score": 20, "max_score": 20, "passed": True, "reason": "文件存在且为合法 JSON"})
            total_score += 20
        except Exception as e:
            details.append({"item": "JSON报告合法性校验", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON 解析失败: {e}"})
    else:
        details.append({"item": "JSON报告合法性校验", "score": 0, "max_score": 20, "passed": False, "reason": "charity_report.json 文件不存在"})

    # 3. Patient List Base (10 pts)
    if agent_data and "patients" in agent_data and isinstance(agent_data["patients"], list):
        p_list = agent_data["patients"]
        score_base = 0
        if len(p_list) > 0:
            score_base += 5
        if p_list == sorted(list(set(p_list))):
            score_base += 5
        details.append({"item": "患者列表基础验证(去重与排序)", "score": score_base, "max_score": 10, "passed": score_base==10, "reason": f"基础得分为 {score_base}"})
        total_score += score_base
    else:
        details.append({"item": "患者列表基础验证(去重与排序)", "score": 0, "max_score": 10, "passed": False, "reason": "patients 字段缺失或类型错误"})

    # 4. Patient List Accuracy (20 pts)
    if agent_data and "patients" in agent_data and isinstance(agent_data["patients"], list):
        p_list = agent_data["patients"]
        set_gt = set(gt_patients)
        set_ag = set(p_list)
        if set_gt == set_ag:
            details.append({"item": "患者列表精确匹配", "score": 20, "max_score": 20, "passed": True, "reason": "患者集合提取完全正确且过滤精确"})
            total_score += 20
        else:
            union = len(set_gt | set_ag)
            if union > 0:
                intersect = len(set_gt & set_ag)
                match_score = int(20 * (intersect / union))
                details.append({"item": "患者列表精确匹配", "score": match_score, "max_score": 20, "passed": False, "reason": f"未能完全匹配，Jaccard相似度折算部分分: {match_score}"})
                total_score += match_score
            else:
                details.append({"item": "患者列表精确匹配", "score": 0, "max_score": 20, "passed": False, "reason": "无任何相交记录"})
    else:
        details.append({"item": "患者列表精确匹配", "score": 0, "max_score": 20, "passed": False, "reason": "前置条件失败，无法验证匹配度"})

    # 5. Hours Format (10 pts)
    if agent_data and "total_hours" in agent_data:
        val = agent_data["total_hours"]
        if isinstance(val, (int, float)):
            details.append({"item": "累计时长格式验证", "score": 10, "max_score": 10, "passed": True, "reason": "total_hours 存在且为数字类型"})
            total_score += 10
        else:
            details.append({"item": "累计时长格式验证", "score": 0, "max_score": 10, "passed": False, "reason": "total_hours 存在但非数字类型"})
    else:
        details.append({"item": "累计时长格式验证", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 total_hours 字段"})

    # 6. Hours Accuracy (20 pts)
    if agent_data and "total_hours" in agent_data and isinstance(agent_data["total_hours"], (int, float)):
        val = float(agent_data["total_hours"])
        diff = abs(val - gt_hours)
        if diff <= 0.05:
            details.append({"item": "累计时长精度校验", "score": 20, "max_score": 20, "passed": True, "reason": f"总时长计算极其精准，误差 {diff:.3f} 在合理容差内"})
            total_score += 20
        elif diff <= 5.0:
            details.append({"item": "累计时长精度校验", "score": 10, "max_score": 20, "passed": False, "reason": f"有部分偏差(差值 {diff:.3f})，可能时间过滤/单位换算存在遗漏"})
            total_score += 10
        else:
            details.append({"item": "累计时长精度校验", "score": 0, "max_score": 20, "passed": False, "reason": f"计算严重偏差(差值 {diff:.3f})，提取逻辑错误"})
    else:
        details.append({"item": "累计时长精度校验", "score": 0, "max_score": 20, "passed": False, "reason": "前置条件失败，无法验证数值"})

    # 7. Cleanliness & LLM Empathy Check (10 pts)
    # Checks if agent polluted the JSON with extra keys or dropped unsolicited files.
    extra_files = []
    if os.path.exists(admin_dir):
        for f in os.listdir(admin_dir):
            if f != "charity_report.json":
                extra_files.append(f)
                
    extra_keys = []
    if isinstance(agent_data, dict):
        extra_keys = [k for k in agent_data.keys() if k not in ["patients", "total_hours"]]
        
    if not extra_files and not extra_keys:
        details.append({"item": "非结构化要求(报告纯净度)检测", "score": 10, "max_score": 10, "passed": True, "reason": "报告极为纯净，未捏造多余字段，且未遗留冗余文件，完美遵从'clean JSON'指令"})
        total_score += 10
    else:
        # Prompt explicitly mandates checking extra natural language for empathetic response
        content_to_judge = ""
        if extra_keys and agent_data:
            content_to_judge += "Extra JSON Keys Data:\n"
            for k in extra_keys:
                content_to_judge += f"{k}: {agent_data[k]}\n"
        for ef in extra_files:
            ef_path = os.path.join(admin_dir, ef)
            try:
                with open(ef_path, "r", encoding="utf-8") as fp:
                    content_to_judge += f"\nFile {ef} Content:\n{fp.read()[:500]}"
            except:
                pass
                
        llm_prompt = (
            "The AI agent was asked to output a clean JSON report, but generated extra fields or files. "
            "The user persona 'Aris' was extremely stressed, panicked, and mentioned he was 'going to lose his mind'. "
            "Does this extra generated text clearly contain comforting, sympathetic, or reassuring messages directly addressing the doctor's heavy workload and stress? Answer YES or NO."
        )
        is_comforting = llm_judge_content(llm_prompt, content_to_judge)
        if is_comforting:
            details.append({"item": "非结构化要求(报告纯净度)检测", "score": 5, "max_score": 10, "passed": True, "reason": "包含多余字段/文件(未完全遵守clean report)，但利用大模型检测到对医生有正面安抚的说明，给予部分宽慰分数5分"})
            total_score += 5
        else:
            details.append({"item": "非结构化要求(报告纯净度)检测", "score": 0, "max_score": 10, "passed": False, "reason": "包含多余且无意义的数据/文本，利用大模型判定其不仅违反'clean'约束，也未体现任何情感安抚价值，直接0分"})

    # Final summary output
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
