import os
import sys
import json
import csv
import re
from datetime import datetime
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
    # 此函数为检测非结构化文本的统一接口
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
    logs_dir = os.path.join(workspace, "server_logs")
    artifacts_dir = os.path.join(workspace, "artifact_submissions")
    
    # 1. Parse RSVP
    guest_rsvps = {}
    pattern = re.compile(r"\[(.*?)\] \[RSVP-TICKET\] GuestName: (.*?) \| Status: (.*?) \| Extra: (\d+)")
    
    if os.path.exists(logs_dir):
        for root, _, files in os.walk(logs_dir):
            for f in files:
                try:
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                        for line in file:
                            if "[RSVP-TICKET]" in line:
                                match = pattern.search(line)
                                if match:
                                    ts_str, guest, status, extra = match.groups()
                                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                                    if guest not in guest_rsvps or ts > guest_rsvps[guest]['ts']:
                                        guest_rsvps[guest] = {
                                            'ts': ts,
                                            'status': status,
                                            'extra': int(extra)
                                        }
                except Exception:
                    pass

    # 2. Parse Artifacts
    approved_guests = set()
    if os.path.exists(artifacts_dir):
        for root, _, files in os.walk(artifacts_dir):
            for f in files:
                if f.endswith('.csv'):
                    try:
                        with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                            reader = csv.DictReader(file)
                            for row in reader:
                                if row.get('Status') == 'Approved':
                                    approved_guests.add(row.get('GuestName'))
                    except Exception:
                        pass
                            
    # 3. Intersect
    vips = []
    total_headcount = 0
    for guest, data in guest_rsvps.items():
        if data['status'] == 'Confirmed' and guest in approved_guests:
            vips.append(guest)
            total_headcount += (1 + data['extra'])
            
    return sorted(vips), total_headcount

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_dir = os.path.join(workspace, "event_prep")
    target_file = os.path.join(target_dir, "final_vip_list.json")

    details = []
    total_score = 0

    # 预计算 Ground Truth
    gt_vips, gt_headcount = compute_ground_truth(workspace)

    # 验证维度 1: 目录存在性 (10分)
    if os.path.isdir(target_dir):
        details.append({"item": "检查目标目录 event_prep 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 event_prep 存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标目录 event_prep 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录 event_prep 不存在"})

    # 验证维度 2: 文件存在性及合法性 (10分)
    agent_data = None
    if os.path.isfile(target_file):
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                agent_data = json.load(f)
            details.append({"item": "检查 final_vip_list.json 是否为有效JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且格式合法"})
            total_score += 10
        except json.JSONDecodeError:
            details.append({"item": "检查 final_vip_list.json 是否为有效JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件存在但无法解析为合法JSON"})
    else:
        details.append({"item": "检查 final_vip_list.json 是否为有效JSON", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 final_vip_list.json 文件"})

    # 验证维度 3: JSON字段完备且无幻觉 (10分)
    if agent_data is not None and isinstance(agent_data, dict):
        keys = set(agent_data.keys())
        expected_keys = {"vips", "total_headcount"}
        if keys == expected_keys:
            details.append({"item": "检查JSON Schema合法性及严禁伪造冗余字段", "score": 10, "max_score": 10, "passed": True, "reason": "恰好包含要求的两个字段，无冗余/幻觉"})
            total_score += 10
        elif expected_keys.issubset(keys):
            details.append({"item": "检查JSON Schema合法性及严禁伪造冗余字段", "score": 0, "max_score": 10, "passed": False, "reason": f"存在未被要求的伪造字段: {keys - expected_keys}"})
        else:
            details.append({"item": "检查JSON Schema合法性及严禁伪造冗余字段", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少必备字段: {expected_keys - keys}"})
    else:
        details.append({"item": "检查JSON Schema合法性及严禁伪造冗余字段", "score": 0, "max_score": 10, "passed": False, "reason": "JSON根节点必须是字典形式"})

    # 验证维度 4 & 5: VIP人员名单精准匹配与排序 (40分 + 10分)
    agent_vips = []
    if agent_data is isinstance(agent_data, dict) and "vips" in agent_data and isinstance(agent_data["vips"], list):
        agent_vips = [str(x) for x in agent_data["vips"]]
        gt_set = set(gt_vips)
        agent_set = set(agent_vips)
        
        union_len = len(gt_set.union(agent_set))
        if union_len == 0:
            vip_score = 40 if len(gt_set) == 0 else 0
        else:
            intersection_len = len(gt_set.intersection(agent_set))
            vip_score = int(40 * (intersection_len / union_len))
        
        details.append({"item": "VIP名单精准度 (IoU打分)", "score": vip_score, "max_score": 40, "passed": vip_score == 40, "reason": f"真实名单 {len(gt_set)} 人，提交名单 {len(agent_set)} 人，匹配度得分 {vip_score}/40"})
        total_score += vip_score

        # 排序检查
        if agent_vips == sorted(agent_vips) and len(agent_vips) > 0:
            details.append({"item": "检查VIP名单是否按照字母顺序排序", "score": 10, "max_score": 10, "passed": True, "reason": "VIP名单排序正确"})
            total_score += 10
        else:
            details.append({"item": "检查VIP名单是否按照字母顺序排序", "score": 0, "max_score": 10, "passed": False, "reason": "未做字母排序，或列表为空"})
    else:
         details.append({"item": "VIP名单精准度及排序", "score": 0, "max_score": 50, "passed": False, "reason": "未找到合法的vips列表字段"})

    # 验证维度 6: Total Headcount 计算准确性 (20分)
    if agent_data is isinstance(agent_data, dict) and "total_headcount" in agent_data:
        try:
            agent_headcount = int(agent_data["total_headcount"])
            diff = abs(agent_headcount - gt_headcount)
            if diff == 0:
                hc_score = 20
                reason = "宾客总人数(含Extra)计算完全准确"
            elif diff <= 3:
                hc_score = 10
                reason = f"总人数存在细微误差 (偏差值: {diff})"
            else:
                hc_score = 0
                reason = f"总人数计算错误 (提交: {agent_headcount}, 真实: {gt_headcount})"
            details.append({"item": "验证总宾客数计算精度", "score": hc_score, "max_score": 20, "passed": hc_score == 20, "reason": reason})
            total_score += hc_score
        except ValueError:
            details.append({"item": "验证总宾客数计算精度", "score": 0, "max_score": 20, "passed": False, "reason": "total_headcount 字段并非合法整数"})
    else:
        details.append({"item": "验证总宾客数计算精度", "score": 0, "max_score": 20, "passed": False, "reason": "未找到合法的 total_headcount 字段"})

    # 写入最终分数结果文件
    with open("workplace_score.json", "w", encoding="utf-8") as out:
        json.dump({
            "total_score": total_score,
            "details": details
        }, out, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
