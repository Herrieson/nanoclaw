import os
import sys
import json
import httpx
import re
import csv
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

def get_ground_truth(workspace):
    csv_path = os.path.join(workspace, 'front_desk', 'master_work_orders_2023.csv')
    if not os.path.exists(csv_path):
        return None, None
    
    transmission_wos = set()
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Job_Category') == 'Transmission':
                    transmission_wos.add(row.get('WO_ID'))
    except Exception:
        return None, None
    
    total_hours = 0.0
    total_quarts = 0.0
    
    shop_notes_dir = os.path.join(workspace, 'shop_notes')
    if not os.path.exists(shop_notes_dir):
        return None, None
        
    try:
        for root, dirs, files in os.walk(shop_notes_dir):
            for file in files:
                if file.endswith('.txt'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 按段落切分以保证工单文本块不会互相污染
                        paragraphs = content.split('\n\n')
                        for p in paragraphs:
                            match_wo = re.search(r'WO-\d+', p)
                            if match_wo:
                                wo_id = match_wo.group(0)
                                if wo_id in transmission_wos:
                                    h_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:hrs|hours)', p, re.IGNORECASE)
                                    if h_match:
                                        total_hours += float(h_match.group(1))
                                    q_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:quarts|qts)', p, re.IGNORECASE)
                                    if q_match:
                                        total_quarts += float(q_match.group(1))
        return total_hours, total_quarts
    except Exception:
        return None, None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    details = []
    total_score = 0
    target_file = os.path.join(workspace, 'office_reports', 'transmission_summary.json')

    # 1. 检查目标文件是否存在 (10分)
    if os.path.exists(target_file):
        details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 transmission_summary.json 存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 transmission_summary.json 不存在"})
        
    agent_json = None
    file_content = ""
    
    if os.path.exists(target_file):
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            # 2. 检查文件是否为合法JSON (10分)
            agent_json = json.loads(file_content)
            details.append({"item": "检查文件是否为合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件格式是合法的 JSON"})
            total_score += 10
        except json.JSONDecodeError:
            details.append({"item": "检查文件是否为合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 解析失败，格式非法"})
            
        # 3. 利用 LLM 检查是否包含多余废话 (10分)
        prompt_text = "The mechanic user explicitly instructed: 'Don't give me any long speeches or explanations, just get it done!' Evaluate the file content below. Does it ONLY contain the raw requested data (JSON block), without any extra conversational text, apologies, greetings, or ranting explanations? Answer YES if it is clean data, or NO if it contains extra speeches or commentary."
        if llm_judge_content(prompt_text, file_content):
            details.append({"item": "检查是否包含多余废话", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定内容干净，无额外废话"})
            total_score += 10
        else:
            details.append({"item": "检查是否包含多余废话", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定文件中包含了违背人设的多余解释或废话"})
    else:
        details.append({"item": "检查文件是否为合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": "目标文件不存在，无法解析"})
        details.append({"item": "检查是否包含多余废话", "score": 0, "max_score": 10, "passed": False, "reason": "目标文件不存在，无法检测"})

    # 4. 检查字段是否严格符合且无捏造 (10分)
    if agent_json is not None and isinstance(agent_json, dict):
        keys = set(agent_json.keys())
        expected_keys = {"total_labor_hours", "total_fluid_quarts"}
        if keys == expected_keys:
            details.append({"item": "检查是否只包含指定字段且无捏造", "score": 10, "max_score": 10, "passed": True, "reason": "字段完全符合预期，没有捏造多余节点"})
            total_score += 10
        elif expected_keys.issubset(keys):
            details.append({"item": "检查是否只包含指定字段且无捏造", "score": 0, "max_score": 10, "passed": False, "reason": f"禁止幻觉: Agent 捏造了多余字段 {keys - expected_keys}"})
        else:
            details.append({"item": "检查是否只包含指定字段且无捏造", "score": 0, "max_score": 10, "passed": False, "reason": "缺失题意明确要求产出的核心字段"})
    else:
        details.append({"item": "检查是否只包含指定字段且无捏造", "score": 0, "max_score": 10, "passed": False, "reason": "非字典结构或未提取到有效 JSON"})

    # 动态计算真值并判断数值结果
    gt_hours, gt_quarts = get_ground_truth(workspace)
    
    if gt_hours is None or gt_quarts is None:
        details.append({"item": "total_labor_hours 精度校验", "score": 0, "max_score": 30, "passed": False, "reason": "原始数据文件缺失或损坏，无法计算真值"})
        details.append({"item": "total_fluid_quarts 精度校验", "score": 0, "max_score": 30, "passed": False, "reason": "原始数据文件缺失或损坏，无法计算真值"})
    else:
        # 5. total_labor_hours (30分)
        if agent_json is not None and isinstance(agent_json, dict) and "total_labor_hours" in agent_json:
            agent_hours = agent_json.get("total_labor_hours")
            if isinstance(agent_hours, (int, float)) and abs(agent_hours - gt_hours) < 0.2:
                details.append({"item": "total_labor_hours 精度校验", "score": 30, "max_score": 30, "passed": True, "reason": f"结果 {agent_hours} 与动态计算真值匹配"})
                total_score += 30
            else:
                details.append({"item": "total_labor_hours 精度校验", "score": 0, "max_score": 30, "passed": False, "reason": f"结果 {agent_hours} 错误，未通过真值比对 (应接近 {gt_hours})"})
        else:
            details.append({"item": "total_labor_hours 精度校验", "score": 0, "max_score": 30, "passed": False, "reason": "JSON中未找到有效的 total_labor_hours 数值"})
            
        # 6. total_fluid_quarts (30分)
        if agent_json is not None and isinstance(agent_json, dict) and "total_fluid_quarts" in agent_json:
            agent_quarts = agent_json.get("total_fluid_quarts")
            if isinstance(agent_quarts, (int, float)) and abs(agent_quarts - gt_quarts) < 0.2:
                details.append({"item": "total_fluid_quarts 精度校验", "score": 30, "max_score": 30, "passed": True, "reason": f"结果 {agent_quarts} 与动态计算真值匹配"})
                total_score += 30
            else:
                details.append({"item": "total_fluid_quarts 精度校验", "score": 0, "max_score": 30, "passed": False, "reason": f"结果 {agent_quarts} 错误，未通过真值比对 (应接近 {gt_quarts})"})
        else:
            details.append({"item": "total_fluid_quarts 精度校验", "score": 0, "max_score": 30, "passed": False, "reason": "JSON中未找到有效的 total_fluid_quarts 数值"})

    # 结果落盘
    report = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
