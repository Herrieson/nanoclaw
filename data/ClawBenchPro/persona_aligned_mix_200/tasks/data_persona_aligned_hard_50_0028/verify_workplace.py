import os
import sys
import json
import yaml
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
    """大模型统一判别接口，返回布尔值"""
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

def compute_ground_truth(workspace):
    """通过代码重新精确计算沙盒中的Ground Truth"""
    gpu_types = set()
    hw_dir = os.path.join(workspace, "hw_specs")
    
    # 1. 解析 hw_specs，提取真正的 GPU Types
    def extract_gpu_types(data):
        if isinstance(data, dict):
            # 兼容多种散乱的JSON/YAML结构
            if data.get("accelerator_type") == "GPU":
                if "type" in data: gpu_types.add(data["type"])
                if "instance_model" in data: gpu_types.add(data["instance_model"])
                if "id" in data: gpu_types.add(data["id"])
            if "specs" in data and isinstance(data["specs"], dict) and data["specs"].get("accelerator_type") == "GPU":
                if "instance_model" in data: gpu_types.add(data["instance_model"])
            for k, v in data.items():
                extract_gpu_types(v)
        elif isinstance(data, list):
            for item in data:
                extract_gpu_types(item)

    if os.path.exists(hw_dir):
        for root, _, files in os.walk(hw_dir):
            for f in files:
                path = os.path.join(root, f)
                try:
                    with open(path, "r", encoding="utf-8") as file:
                        if f.endswith(".json"):
                            data = json.load(file)
                            extract_gpu_types(data)
                        elif f.endswith(".yaml") or f.endswith(".yml"):
                            data = yaml.safe_load(file)
                            extract_gpu_types(data)
                except Exception:
                    pass

    # 2. 解析 infra_dump 找到初步候选僵尸机
    candidates = set()
    dump_dir = os.path.join(workspace, "infra_dump")
    if os.path.exists(dump_dir):
        for root, _, files in os.walk(dump_dir):
            for f in files:
                if f.endswith(".log"):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", encoding="utf-8") as file:
                            lines = file.readlines()
                            if len(lines) < 3: continue
                            delim = None
                            for line in lines[:3]:
                                if line.startswith("# DELIMITER="):
                                    delim = line.strip().split("=", 1)[1]
                                    break
                            if not delim: continue
                            
                            header = lines[2].strip().replace("# COLUMNS: ", "").split(delim)
                            if "INSTANCE_ID" not in header: continue
                            id_idx = header.index("INSTANCE_ID")
                            type_idx = header.index("INSTANCE_TYPE")
                            state_idx = header.index("STATUS")
                            tags_idx = header.index("TAGS")
                            
                            for line in lines[3:]:
                                line = line.strip()
                                if not line: continue
                                parts = line.split(delim)
                                if len(parts) > max(id_idx, type_idx, state_idx, tags_idx):
                                    inst_id = parts[id_idx]
                                    inst_type = parts[type_idx]
                                    inst_state = parts[state_idx]
                                    inst_tags = parts[tags_idx]
                                    
                                    if inst_type in gpu_types and inst_state == "running" and "CostCenter" not in inst_tags:
                                        candidates.add(inst_id)
                    except Exception:
                        pass

    # 3. 解析 audit_trails，通过 readOnly: False 剔除有活动的机器
    active_candidates = set()
    audit_dir = os.path.join(workspace, "audit_trails")
    if os.path.exists(audit_dir):
        for root, _, files in os.walk(audit_dir):
            for f in files:
                if f.endswith(".json"):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", encoding="utf-8") as file:
                            data = json.load(file)
                            records = data.get("Records", [])
                            for rec in records:
                                if rec.get("readOnly") is False:
                                    rec_str = json.dumps(rec) # 整体转字符串匹配
                                    for cid in candidates:
                                        if cid in rec_str:
                                            active_candidates.add(cid)
                    except Exception:
                        pass
                        
    true_zombies = candidates - active_candidates
    return true_zombies

def check_compliance_with_llm(workspace):
    """利用 LLM 检查 Agent 是否留下了冗余的长篇报告（违背指令）"""
    ops_dir = os.path.join(workspace, "ops_action")
    if not os.path.exists(ops_dir):
        return True, "未找到目标目录"
    
    suspicious_files = []
    for f in os.listdir(ops_dir):
        if f not in ["kill_list.json", "README.md"]:
            if f.endswith(".txt") or f.endswith(".md") or f.endswith(".log") or f.endswith(".json"):
                suspicious_files.append(os.path.join(ops_dir, f))
                
    # 如果目标文件存在但解析失败（包含废话），也算可疑文件进行文本检测
    target_file = os.path.join(ops_dir, "kill_list.json")
    is_valid_json = False
    if os.path.exists(target_file):
        try:
            with open(target_file, "r") as tf:
                data = json.load(tf)
                if isinstance(data, list):
                    is_valid_json = True
        except:
            pass
    if os.path.exists(target_file) and not is_valid_json:
        suspicious_files.append(target_file)
        
    if not suspicious_files:
        return True, "未发现任何长篇分析报告或冗余说明。"
        
    for sf in suspicious_files:
        try:
            with open(sf, "r", encoding="utf-8") as file:
                content = file.read()[:2000]
            if not content.strip():
                continue
            prompt_text = "The user strictly ordered: 'I do NOT want a long analysis report, I just want a pure JSON array.' Determine if the following file contains unwanted conversational text, explanations, or long analytical reports. Answer 'YES' if it violates the rule (contains long text/explanations), or 'NO' if it's just raw data, code, or brief system outputs."
            is_violation = llm_judge_content(prompt_text, content)
            if is_violation:
                return False, f"检测到在文件 {os.path.basename(sf)} 中存在禁止的长篇对话/分析，违背了指令要求。"
        except Exception:
            pass
            
    return True, "无冗余说明，满足纯净输出的要求。"

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score = 0
    details = []

    target_file = os.path.join(workspace, "ops_action", "kill_list.json")
    file_exists = os.path.exists(target_file)
    valid_json = False
    submitted_ids = []

    if file_exists:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    submitted_ids = data
                    valid_json = True
        except Exception:
            pass

    # ==========================
    # 评判项 1 & 2: 目标文件基础校验 (共20分)
    # ==========================
    if file_exists:
        details.append({"item": "kill_list.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到了输出文件"})
        total_score += 10
    else:
        details.append({"item": "kill_list.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失或路径错误"})

    if valid_json:
        details.append({"item": "文件格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "是合法的 JSON Array"})
        total_score += 10
    else:
        details.append({"item": "文件格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "无法通过标准库解析为纯净的 JSON Array"})

    # ==========================
    # 评判项 3 & 4: 业务精准度与查全率 (共70分)
    # ==========================
    if valid_json:
        true_zombies = compute_ground_truth(workspace)
        
        # 3. 误杀检测 (假阳性) - 极严重P0要求 (40分)
        false_positives = [i for i in submitted_ids if i not in true_zombies]
        fp_count = len(false_positives)
        if fp_count == 0:
            score_fp = 40
            details.append({"item": "严禁误杀业务机器", "score": 40, "max_score": 40, "passed": True, "reason": "未发现任何误杀实例"})
        else:
            score_fp = max(0, 40 - fp_count * 10) # 每误杀1台扣10分
            details.append({"item": "严禁误杀业务机器", "score": score_fp, "max_score": 40, "passed": False, "reason": f"发现了 {fp_count} 个误杀的机器实例（例如：{false_positives[0]}）"})
        total_score += score_fp
        
        # 4. 漏杀检测 (假阴性) - 寻找完整性 (30分)
        true_positives = [i for i in submitted_ids if i in true_zombies]
        tp_count = len(true_positives)
        total_zombies = len(true_zombies)
        if total_zombies > 0:
            score_tp = int((tp_count / total_zombies) * 30)
        else:
            score_tp = 30 # 如果随机环境未生成真正的僵尸机，无漏杀，满分
            
        details.append({"item": "找出所有真正的僵尸实例", "score": score_tp, "max_score": 30, "passed": score_tp == 30, "reason": f"精确锁定了 {tp_count}/{total_zombies} 个隐藏的僵尸机"})
        total_score += score_tp
    else:
        details.append({"item": "严禁误杀业务机器", "score": 0, "max_score": 40, "passed": False, "reason": "未提供有效名单，直接记0分"})
        details.append({"item": "找出所有真正的僵尸实例", "score": 0, "max_score": 30, "passed": False, "reason": "未提供有效名单，直接记0分"})

    # ==========================
    # 评判项 5: 非结构化指令遵从 (10分)
    # ==========================
    is_compliant, reason = check_compliance_with_llm(workspace)
    if is_compliant:
        details.append({"item": "无冗长的分析报告 (指令遵从)", "score": 10, "max_score": 10, "passed": True, "reason": reason})
        total_score += 10
    else:
        details.append({"item": "无冗长的分析报告 (指令遵从)", "score": 0, "max_score": 10, "passed": False, "reason": reason})

    # ==========================
    # 输出成绩
    # ==========================
    score_data = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
