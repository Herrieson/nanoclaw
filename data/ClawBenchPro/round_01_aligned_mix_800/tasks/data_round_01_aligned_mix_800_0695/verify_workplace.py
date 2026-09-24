import os
import sys
import json
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

def get_all_numbers(node):
    """递归提取节点中的所有数字以供精准比对，防范幻觉"""
    nums = []
    if isinstance(node, dict):
        for v in node.values():
            if isinstance(v, (int, float)):
                nums.append(float(v))
            elif isinstance(v, str):
                try:
                    nums.append(float(v))
                except ValueError:
                    pass
            elif isinstance(v, (dict, list)):
                nums.extend(get_all_numbers(v))
    elif isinstance(node, list):
        for item in node:
            nums.extend(get_all_numbers(item))
    return nums

def check_entity(data, name, id_str, expected_actual, expected_scheduled):
    """使用确定的逻辑在未知结构的JSON中匹配实体及其对应的工时数值，避免单纯的字符串查找带来的假阳性"""
    def find_entity_nodes(node):
        found = []
        if isinstance(node, dict):
            # 将当前层的 keys 和 字符串 values 打平
            keys_vals = [str(k).lower() for k in node.keys()] + [str(v).lower() for v in node.values() if isinstance(v, str)]
            if name.lower() in keys_vals or id_str.lower() in keys_vals:
                found.append(node)
            for v in node.values():
                found.extend(find_entity_nodes(v))
        elif isinstance(node, list):
            for item in node:
                found.extend(find_entity_nodes(item))
        return found

    nodes = find_entity_nodes(data)
    for node in nodes:
        nums = get_all_numbers(node)
        # 必须在该实体的上下文中准确包含实际工时和排班工时的具体数值
        if expected_actual in nums and expected_scheduled in nums:
            return True
    return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 1. 检查 deliverables/payroll_final.json 存在且格式合法 (10分)
    json_path = os.path.join(workspace, "deliverables", "payroll_final.json")
    payroll_data = None
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                payroll_data = json.load(f)
            results.append({"item": "检查 payroll_final.json 存在且是合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且格式正确"})
            total_score += 10
        except json.JSONDecodeError:
            results.append({"item": "检查 payroll_final.json 存在且是合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件存在但不是合法的 JSON，判定格式损坏"})
    else:
        results.append({"item": "检查 payroll_final.json 存在且是合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "未找到要求的 JSON 结果文件"})

    # 2. 检查 JSON 中是否包含结构化与清洁过的工时数据 (30分)
    alice_passed = bob_passed = charlie_passed = False
    if payroll_data is not None:
        if check_entity(payroll_data, "Alice", "E001", 42, 40):
            alice_passed = True
            total_score += 10
        if check_entity(payroll_data, "Bob", "E002", 25, 20):
            bob_passed = True
            total_score += 10
        if check_entity(payroll_data, "Charlie", "E003", 30, 30):
            charlie_passed = True
            total_score += 10
            
    results.append({"item": "检查JSON中包含Alice准确的实际打卡(42h)与排班(40h)", "score": 10 if alice_passed else 0, "max_score": 10, "passed": alice_passed, "reason": "成功提取准确数值" if alice_passed else "未正确提取出对应的数值或结构混乱"})
    results.append({"item": "检查JSON中包含Bob准确的实际打卡(25h)与排班(20h)", "score": 10 if bob_passed else 0, "max_score": 10, "passed": bob_passed, "reason": "成功提取准确数值" if bob_passed else "未正确提取出对应的数值或结构混乱"})
    results.append({"item": "检查JSON中包含Charlie准确的实际打卡(30h)与排班(30h)", "score": 10 if charlie_passed else 0, "max_score": 10, "passed": charlie_passed, "reason": "成功提取准确数值" if charlie_passed else "未正确提取出对应的数值或结构混乱"})

    # 3. 检查 audit_summary.txt 存在 (10分)
    txt_path = os.path.join(workspace, "deliverables", "audit_summary.txt")
    txt_content = ""
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            txt_content = f.read()
        results.append({"item": "检查 audit_summary.txt 文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "总结报告存在"})
        total_score += 10
    else:
        results.append({"item": "检查 audit_summary.txt 文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到总结报告"})

    # 4. LLM 对非结构化语义的检测 (50分)
    if txt_content:
        # LLM 判断 1: 指出 Dave 为幽灵员工 (15分)
        p1 = "Does the following report explicitly state that 'Dave' (or E004) is a 'ghost employee' (meaning he punched in without being scheduled) AND mention that he logged exactly 5 hours?"
        if llm_judge_content(p1, txt_content):
            results.append({"item": "报告指出Dave是幽灵员工并说明其打卡5小时", "score": 15, "max_score": 15, "passed": True, "reason": "大模型判定报告指出了关键异常"})
            total_score += 15
        else:
            results.append({"item": "报告指出Dave是幽灵员工并说明其打卡5小时", "score": 0, "max_score": 15, "passed": False, "reason": "大模型未检测到对该员工准确的幽灵指控"})
            
        # LLM 判断 2: 指出 Bob 的超时情况 (15分)
        p2 = "Does the report explicitly identify 'Bob' (or E002) as having actual worked hours exceeding his scheduled hours by more than 10%? It must mention his scheduled hours (20) and actual hours (25)."
        if llm_judge_content(p2, txt_content):
            results.append({"item": "报告指出Bob工时超出排班10%并列出对应工时", "score": 15, "max_score": 15, "passed": True, "reason": "大模型判定报告找出了合规性差错"})
            total_score += 15
        else:
            results.append({"item": "报告指出Bob工时超出排班10%并列出对应工时", "score": 0, "max_score": 15, "passed": False, "reason": "大模型判定缺失对Bob的准确分析或未点明10%超限"})

        # LLM 判断 3: 完美代入严格财务主管的Persona (20分)
        p3 = "Does this report sound like it was written by a meticulous 54-year-old female bookkeeper? Does it contain a strict, somewhat complaining tone about 'young people' or 'newcomers' being careless, messy, or sloppy with the data? (A factual but bland report WITHOUT this persona flavor MUST be judged as NO)."
        if llm_judge_content(p3, txt_content):
            results.append({"item": "报告包含54岁严厉簿记员的独特语气特征", "score": 20, "max_score": 20, "passed": True, "reason": "情感和语气完美契合设定要求"})
            total_score += 20
        else:
            results.append({"item": "报告包含54岁严厉簿记员的独特语气特征", "score": 0, "max_score": 20, "passed": False, "reason": "行文平淡，未充分展现指定的长者和严格财务人员的口吻"})
    else:
        results.append({"item": "报告指出Dave是幽灵员工并说明其打卡5小时", "score": 0, "max_score": 15, "passed": False, "reason": "无报告内容可供检测"})
        results.append({"item": "报告指出Bob工时超出排班10%并列出对应工时", "score": 0, "max_score": 15, "passed": False, "reason": "无报告内容可供检测"})
        results.append({"item": "报告包含54岁严厉簿记员的独特语气特征", "score": 0, "max_score": 20, "passed": False, "reason": "无报告内容可供检测"})

    final_output = {
        "total_score": total_score,
        "details": results
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
