import os
import sys
import json
import csv
import glob
import httpx
from openai import OpenAI

# 🔒 强制 API 规范
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

def calculate_expected_data(workspace):
    # 模拟 env_builder 的逻辑来计算预期结果
    clients = {}
    client_dir = os.path.join(workspace, 'CLIENT_DATA_ARCHIVE')
    for root, dirs, files in os.walk(client_dir):
        for f in files:
            if f.endswith('.json'):
                with open(os.path.join(root, f), 'r') as jf:
                    data = json.load(jf)
                    if 'name' in data and data.get('meta', {}).get('rsvp') is True:
                        clients[data['name']] = {"diet": data['meta'].get('diet'), "calories": 0.0}

    recovery_dir = os.path.join(workspace, 'RECOVERY_DUMP_0524')
    for root, dirs, files in os.walk(recovery_dir):
        for f in files:
            path = os.path.join(root, f)
            try:
                if f.endswith('.csv'):
                    with open(path, 'r') as cf:
                        reader = csv.DictReader(cf)
                        if 'checksum' in reader.fieldnames:
                            for row in reader:
                                if row.get('status') == 'completed' and row['user'] in clients:
                                    cal = (float(row['hr_avg']) - 60) * float(row['duration']) * 0.15
                                    clients[row['user']]["calories"] += cal
                elif f.endswith('.txt'):
                    with open(path, 'r') as tf:
                        content = tf.read()
                        if 'CHK:' in content:
                            lines = content.split('\n')
                            for line in lines:
                                if "USER:" in line and "STAT:completed" in line:
                                    # USER:David|DUR:40|HR:150|STAT:completed|CHK:CRC32_A1
                                    parts = {p.split(':')[0]: p.split(':')[1] for p in line.split('|')}
                                    user = parts['USER']
                                    if user in clients:
                                        cal = (float(parts['HR']) - 60) * float(parts['DUR']) * 0.15
                                        clients[user]["calories"] += cal
                else:
                    # JSON check
                    with open(path, 'r') as jf:
                        data = json.load(jf)
                        if isinstance(data, list) and any('checksum' in item for item in data):
                            for item in data:
                                if item.get('status') == 'completed' and item['user'] in clients:
                                    cal = (float(item['hr_avg']) - 60) * float(item['duration']) * 0.15
                                    clients[item['user']]["calories"] += cal
            except:
                continue
    
    # 过滤没有记录或不符合条件的
    final = {}
    for name, info in clients.items():
        final[name] = {"full_name": name, "total_calories_burned": info["calories"], "dietary_needs": info["diet"]}
    return final

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = os.path.join(workspace, "party_prep/final_report.json")
    score_details = []
    total_score = 0

    # 1. 基础结构检查 (10分)
    if os.path.exists(output_file):
        score_details.append({"item": "文件生成", "score": 10, "max_score": 10, "passed": True, "reason": "文件已生成在指定目录"})
        total_score += 10
    else:
        score_details.append({"item": "文件生成", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 party_prep/final_report.json"})
        # 写入并退出
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return

    # 2. 格式合法性与字段检查 (20分)
    try:
        with open(output_file, 'r') as f:
            agent_data = json.load(f)
        
        if isinstance(agent_data, list):
            fields_ok = True
            for entry in agent_data:
                if not all(k in entry for k in ["full_name", "total_calories_burned", "dietary_needs"]):
                    fields_ok = False
                    break
            if fields_ok:
                score_details.append({"item": "JSON结构与字段完整性", "score": 20, "max_score": 20, "passed": True, "reason": "字段完全符合Prompt要求"})
                total_score += 20
            else:
                score_details.append({"item": "JSON结构与字段完整性", "score": 5, "max_score": 20, "passed": False, "reason": "部分条目缺失必要字段"})
        else:
            score_details.append({"item": "JSON结构", "score": 0, "max_score": 20, "passed": False, "reason": "输出不是 JSON 列表"})
    except Exception as e:
        score_details.append({"item": "JSON解析", "score": 0, "max_score": 20, "passed": False, "reason": f"解析失败: {str(e)}"})

    # 3. 逻辑过滤与计算准确性 (50分)
    expected_data = calculate_expected_data(workspace)
    
    agent_dict = {item['full_name']: item for item in agent_data if 'full_name' in item}
    
    # 检查 RSVP 过滤
    wrong_rsvp = [name for name in agent_dict if name not in expected_data]
    missed_rsvp = [name for name in expected_data if name not in agent_dict]
    
    calc_score = 0
    if not wrong_rsvp and not missed_rsvp:
        calc_score += 20 # RSVP 过滤正确
    elif len(wrong_rsvp) < 2 and len(missed_rsvp) < 2:
        calc_score += 10
        
    # 检查卡路里计算 (公式：(HR-60)*DUR*0.15)
    precision_errors = 0
    for name, exp_val in expected_data.items():
        if name in agent_dict:
            if abs(agent_dict[name]['total_calories_burned'] - exp_val['total_calories_burned']) > 0.1:
                precision_errors += 1
    
    if precision_errors == 0 and len(agent_dict) == len(expected_data):
        calc_score += 30
    elif precision_errors < 2:
        calc_score += 15
        
    score_details.append({"item": "业务逻辑与数值计算", "score": calc_score, "max_score": 50, "passed": calc_score == 50, "reason": f"RSVP过滤错误数:{len(wrong_rsvp)+len(missed_rsvp)}, 计算误差数:{precision_errors}"})
    total_score += calc_score

    # 4. LLM 语义校验：膳食需求对应 (20分)
    # 抽取部分数据让 LLM 确认是否正确提取了 diet 字段而不是垃圾数据
    sample_content = json.dumps(agent_data[:3], ensure_content_type=False) if agent_data else "Empty"
    llm_prompt = "Verify if the 'dietary_needs' field contains valid dietary information (e.g., Vegan, Nut Allergy, None) rather than random hash keys or system errors."
    if llm_judge_content(llm_prompt, sample_content):
        score_details.append({"item": "膳食需求语义校验", "score": 20, "max_score": 20, "passed": True, "reason": "大模型确认提取的是真实的膳食需求文本"})
        total_score += 20
    else:
        score_details.append({"item": "膳食需求语义校验", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定膳食需求字段包含噪音或错误信息"})

    # Final Write
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(total_score), "details": score_details}, f)

if __name__ == "__main__":
    main()
