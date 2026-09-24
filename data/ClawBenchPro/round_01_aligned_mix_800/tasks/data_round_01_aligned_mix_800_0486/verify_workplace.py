import os
import sys
import json
import csv
import re
import httpx
from openai import OpenAI

# =====================================================================
# 强制 API 规范初始化 (LLM 探针保留接口)
# =====================================================================
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
    """
    非结构化文本语义检测接口。由于本任务主要考察数据清洗与深度挖掘，
    核心探针基于纯净代码；此函数保留用于可能的扩展审查（如防注入、防幻觉）。
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
# 核心业务逻辑：通过原生代码严格重建 Ground Truth (严防幻觉与假阴性)
# =====================================================================
def get_ground_truth(workspace):
    uncleared_names = []
    consultation_names = []
    
    # -------------------------------------------------------------
    # 链路 A: 志愿者身份与安全审计比对
    # -------------------------------------------------------------
    target_vols = {} # vol_id: name
    signup_dir = os.path.join(workspace, "district_system/volunteer_portal/signups")
    if os.path.exists(signup_dir):
        for root, _, files in os.walk(signup_dir):
            for f in files:
                path = os.path.join(root, f)
                if f.endswith('.json'):
                    try:
                        with open(path, 'r', encoding='utf-8') as jf:
                            data = json.load(jf)
                            if str(data.get("signup_year")) == "2024" and data.get("target_event") == "Spring_Showcase":
                                target_vols[data["vol_id"]] = data["full_name"]
                    except: pass
                elif f.endswith('.csv'):
                    try:
                        with open(path, 'r', encoding='utf-8') as cf:
                            reader = csv.DictReader(cf)
                            for row in reader:
                                if str(row.get("year", "")) == "2024" and row.get("event") == "Spring_Showcase":
                                    target_vols[row["id"]] = row["name"]
                    except: pass

    cleared_vols = set()
    audit_dir = os.path.join(workspace, "district_system/security_audits")
    if os.path.exists(audit_dir):
        for root, _, files in os.walk(audit_dir):
            for f in files:
                if f.endswith('.log'):
                    try:
                        with open(os.path.join(root, f), 'r', encoding='utf-8') as lf:
                            for line in lf:
                                if "STATUS: CLEARED" in line:
                                    # Example: VERIFICATION ID: V-12345 - STATUS: CLEARED - VALID_UNTIL: 2024-12-31
                                    m = re.search(r"VERIFICATION ID:\s*(V-\d+).*?VALID_UNTIL:\s*(\d{4})", line)
                                    if m:
                                        vol_id, year = m.group(1), int(m.group(2))
                                        if year >= 2024:
                                            cleared_vols.add(vol_id)
                    except: pass
                    
    for vid, vname in target_vols.items():
        if vid not in cleared_vols:
            uncleared_names.append(vname)
            
    uncleared_names = sorted(list(set(uncleared_names)))

    # -------------------------------------------------------------
    # 链路 B: 学生信息、医疗记录与政策白名单跨表三段跳
    # -------------------------------------------------------------
    policies = {}
    policy_dir = os.path.join(workspace, "district_system/policies/accessibility")
    if os.path.exists(policy_dir):
        for root, _, files in os.walk(policy_dir):
            for f in files:
                if f.endswith('.json'): # 忽略 YAML 噪音
                    try:
                        with open(os.path.join(root, f), 'r', encoding='utf-8') as jf:
                            data = json.load(jf)
                            policies[data.get("motor_level")] = data.get("allowed_instruments", [])
                    except: pass

    target_students = {}
    prof_dir = os.path.join(workspace, "district_system/student_profiles")
    if os.path.exists(prof_dir):
        for root, _, files in os.walk(prof_dir):
            for f in files:
                if f.endswith('.json'):
                    try:
                        with open(os.path.join(root, f), 'r', encoding='utf-8') as jf:
                            data = json.load(jf)
                            if data.get("status") == "active" and "showcase_request" in data:
                                inst_code = data["showcase_request"].get("instrument_code")
                                if inst_code:
                                    target_students[data.get("student_id")] = {
                                        "name": data.get("name"),
                                        "requested_inst": inst_code
                                    }
                    except: pass

    eval_dir = os.path.join(workspace, "district_system/medical_evaluations")
    if os.path.exists(eval_dir):
        for root, _, files in os.walk(eval_dir):
            for f in files:
                if f.endswith('.txt'):
                    try:
                        with open(os.path.join(root, f), 'r', encoding='utf-8') as tf:
                            content = tf.read()
                            id_m = re.search(r"Patient_ID:\s*(S-\d+)", content)
                            lvl_m = re.search(r"Motor_Skill_Level:\s*(LEVEL_\d+)", content)
                            if id_m and lvl_m:
                                sid, lvl = id_m.group(1), lvl_m.group(1)
                                if sid in target_students:
                                    target_students[sid]["motor_lvl"] = lvl
                    except: pass

    for sid, info in target_students.items():
        req = info.get("requested_inst")
        lvl = info.get("motor_lvl")
        # 如果未找到合法等级或请求不在白名单，均需要 consultation
        if lvl not in policies or req not in policies[lvl]:
            consultation_names.append(info["name"])

    consultation_names = sorted(list(set(consultation_names)))

    return uncleared_names, consultation_names

# =====================================================================
# 验证执行器
# =====================================================================
def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    
    # 1. 结构验证: 目录 (10分)
    prep_dir = os.path.join(workspace, "showcase_prep")
    if os.path.isdir(prep_dir):
        results.append({"item": "检查工作区是否创建 showcase_prep 目录", "score": 10, "max_score": 10, "passed": True, "reason": "目录 showcase_prep 存在"})
    else:
        results.append({"item": "检查工作区是否创建 showcase_prep 目录", "score": 0, "max_score": 10, "passed": False, "reason": "目录 showcase_prep 不存在"})

    # 动态生成 Ground Truth
    try:
        truth_unc, truth_con = get_ground_truth(workspace)
    except Exception as e:
        truth_unc, truth_con = [], []

    def check_json_list_file(file_name, truth_list, task_name_cn):
        file_path = os.path.join(prep_dir, file_name)
        
        # Base format scores
        format_score = 0
        f1_score = 0
        sort_score = 0
        
        if not os.path.isfile(file_path):
            return [
                {"item": f"{task_name_cn} 文件存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"{file_name} 文件不存在"},
                {"item": f"{task_name_cn} 数据精确度验证(F1-Score)", "score": 0, "max_score": 30, "passed": False, "reason": "文件缺失，无法进行精确度计算"},
                {"item": f"{task_name_cn} 排序合规性验证", "score": 0, "max_score": 5, "passed": False, "reason": "文件缺失"}
            ]
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list) or not all(isinstance(x, str) for x in data):
                return [
                    {"item": f"{task_name_cn} 文件存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件存在，但 Schema 错误（非纯字符串列表）"},
                    {"item": f"{task_name_cn} 数据精确度验证(F1-Score)", "score": 0, "max_score": 30, "passed": False, "reason": "数据格式不合规，拒绝判分"},
                    {"item": f"{task_name_cn} 排序合规性验证", "score": 0, "max_score": 5, "passed": False, "reason": "数据格式不合规"}
                ]
                
            format_score = 10
            
            # F1 Score Calculation (严格惩罚幻觉，捏造字段和数据会导致严重扣分)
            agent_set = set(data)
            truth_set = set(truth_list)
            
            tp = len(agent_set & truth_set)
            fp = len(agent_set - truth_set)
            fn = len(truth_set - agent_set)
            
            if tp == 0 and fp == 0 and fn == 0:
                f1 = 1.0
            elif tp == 0:
                f1 = 0.0
            else:
                f1 = 2 * tp / (2 * tp + fp + fn)
                
            f1_score = int(30 * f1)
            
            # Sorted strictly
            if data == sorted(data):
                sort_score = 5
                
            return [
                {"item": f"{task_name_cn} 文件存在且格式合法", "score": format_score, "max_score": 10, "passed": True, "reason": "Schema 合法"},
                {"item": f"{task_name_cn} 数据精确度验证(F1-Score)", "score": f1_score, "max_score": 30, "passed": f1_score == 30, "reason": f"F1-Score={f1:.3f} (TP:{tp}, FP:{fp}, FN:{fn})"},
                {"item": f"{task_name_cn} 排序合规性验证", "score": sort_score, "max_score": 5, "passed": sort_score == 5, "reason": "字母升序排列校验通过" if sort_score == 5 else "未正确进行字母升序排列"}
            ]

        except Exception as e:
            return [
                {"item": f"{task_name_cn} 文件存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"无法解析 JSON: {str(e)}"},
                {"item": f"{task_name_cn} 数据精确度验证(F1-Score)", "score": 0, "max_score": 30, "passed": False, "reason": "JSON解析失败"},
                {"item": f"{task_name_cn} 排序合规性验证", "score": 0, "max_score": 5, "passed": False, "reason": "JSON解析失败"}
            ]

    # 运行细粒度验证并组合
    results.extend(check_json_list_file("uncleared_volunteers.json", truth_unc, "志愿者(Uncleared)"))
    results.extend(check_json_list_file("consultation_students.json", truth_con, "学生(Consultation)"))
    
    total_score = sum(r["score"] for r in results)
    
    # 最终输出结果文件
    output_data = {
        "total_score": total_score,
        "details": results
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
