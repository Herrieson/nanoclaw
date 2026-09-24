import os
import sys
import json
import httpx
import re
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

def calculate_ground_truth(workspace):
    """
    动态计算沙盒中的真实答案，因为环境构建时包含随机数。
    """
    qualified_personnel = set()
    
    # 1. 提取当前有效证书人员 (JSON 碎片)
    json_path = os.path.join(workspace, "dump_site/registry/current/auth_fragment_alpha.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                for cert, names in data.items():
                    if cert in ["FiberOptic", "Cat6"]:
                        qualified_personnel.update(names)
        except Exception:
            pass

    # 2. 提取当前有效证书人员 (文本日志碎片)
    txt_path = os.path.join(workspace, "dump_site/registry/current/sys_log_update.txt")
    if os.path.exists(txt_path):
        try:
            with open(txt_path, 'r') as f:
                content = f.read()
                # 根据 env builder 逻辑: ADD_CERT: [Sarah Lee] -> [FiberOptic]
                if "Sarah Lee" in content and "FiberOptic" in content:
                    qualified_personnel.add("Sarah Lee")
        except Exception:
            pass

    # 3. 统计符合条件人员的有效工时
    personnel_hours = {name: 0 for name in qualified_personnel}
    active_dir = os.path.join(workspace, "dump_site/raw_transmissions/active")
    
    if os.path.exists(active_dir):
        for fname in os.listdir(active_dir):
            if not fname.endswith(".txt"):
                continue
            filepath = os.path.join(active_dir, fname)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                # 解析 USER 和 HOURS_PROVIDED
                user_match = re.search(r"USER:\s*(.+)", content)
                hours_match = re.search(r"HOURS_PROVIDED:\s*([^\s]+)", content)
                
                if user_match and hours_match:
                    user = user_match.group(1).strip()
                    hours_str = hours_match.group(1).strip()
                    
                    if user in qualified_personnel:
                        try:
                            h = float(hours_str)
                            if h > 0:
                                personnel_hours[user] += h
                        except ValueError:
                            pass # 忽略 NaN, unknown 等非数字
            except Exception:
                continue
                
    grand_total = sum(personnel_hours.values())
    return qualified_personnel, personnel_hours, grand_total


def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    
    # 获取 Ground Truth
    expected_qualified, expected_hours, expected_total = calculate_ground_truth(workspace)
    
    # ===== 检测项 1：目录与文件生成 (15分) =====
    target_dir = os.path.join(workspace, "operational_plan")
    target_file = os.path.join(target_dir, "rack_shift_manifest.txt")
    
    if os.path.isdir(target_dir) and os.path.isfile(target_file):
        results.append({"item": "目录与文件生成", "score": 15, "max_score": 15, "passed": True, "reason": "文件和目录结构正确。"})
        total_score += 15
    else:
        results.append({"item": "目录与文件生成", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 operational_plan/rack_shift_manifest.txt。"})
        # 核心文件缺失，直接结束
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": results}, f, indent=2)
        return

    # 读取文件内容
    with open(target_file, "r") as f:
        file_content = f.read()
        
    # ===== 检测项 2：不合格人员剔除 (15分) =====
    # 检查是否误包含了不受欢迎的人员（来自 legacy 或 corrupted，或无效姓名）
    unauthorized = ["Old Man Jenkins", "Zack W", "Alex P", "Linda B"]
    found_unauth = [name for name in unauthorized if name in file_content]
    
    if not found_unauth:
        results.append({"item": "噪音与过期数据剔除", "score": 15, "max_score": 15, "passed": True, "reason": "未发现不合格或过期人员名单。"})
        total_score += 15
    else:
        results.append({"item": "噪音与过期数据剔除", "score": 0, "max_score": 15, "passed": False, "reason": f"包含未授权或过期人员: {found_unauth}。"})

    # ===== 检测项 3：总工时计算准确性 (30分) =====
    # 检测文件中是否包含精确的总分数数字（整数或浮点）
    formatted_total = f"{expected_total:g}" if expected_total.is_integer() else f"{expected_total}"
    if formatted_total in file_content or str(int(expected_total)) in file_content:
        results.append({"item": "总工时计算", "score": 30, "max_score": 30, "passed": True, "reason": f"成功计算并包含正确的总工时 ({formatted_total})。"})
        total_score += 30
    else:
        results.append({"item": "总工时计算", "score": 0, "max_score": 30, "passed": False, "reason": f"未能在文件中找到正确的总工时。期望值: {formatted_total}。"})

    # ===== 检测项 4：个人详细工时与排序 (20分) =====
    # 1. 检查所有的合格人员是否都在文件中，且他们的分项分数是否正确
    # 2. 检查他们的名字在文件中是否按字母顺序排列
    missing_or_wrong = []
    person_positions = {}
    
    for person, hours in expected_hours.items():
        if person not in file_content:
            missing_or_wrong.append(f"{person}(missing)")
            continue
            
        person_positions[person] = file_content.index(person)
        # 查找该人名附近的数字
        # 使用正则在人名同一行找数字
        lines = file_content.split('\n')
        line_with_person = next((line for line in lines if person in line), "")
        formatted_h = f"{hours:g}" if isinstance(hours, float) and hours.is_integer() else str(hours)
        
        # 弱化严格正则匹配格式，只需同行的数值匹配即可
        if formatted_h not in line_with_person:
             missing_or_wrong.append(f"{person}(wrong_hours:{formatted_h} expected)")

    sorted_names_expected = sorted(person_positions.keys())
    sorted_names_actual = sorted(person_positions.keys(), key=lambda x: person_positions[x])
    
    is_sorted = (sorted_names_expected == sorted_names_actual) and len(person_positions) > 0
    
    sub_score = 0
    reason_parts = []
    if not missing_or_wrong:
        sub_score += 15
        reason_parts.append("各个人员名单及统计正确")
    else:
        reason_parts.append(f"名单或数值错误: {missing_or_wrong}")
        
    if is_sorted:
        sub_score += 5
        reason_parts.append("按字母顺序排列成功")
    else:
        reason_parts.append("未按字母顺序排列")

    results.append({"item": "个人明细及排序", "score": sub_score, "max_score": 20, "passed": (sub_score == 20), "reason": "；".join(reason_parts)})
    total_score += sub_score

    # ===== 检测项 5：LLM 语义格式审查 (20分) =====
    # 检查文本是否是一份合格的报告/名册（无废话，且清晰表达出核心排班名册的意思）
    prompt = """Does this text look like a clean, professional personnel roster or manifest? 
It should clearly list people and their hours, and state a grand total. 
It MUST NOT contain agent internal thoughts, conversational fluff (like "Here is your file"), or hallucinated fictional background lore. Answer YES or NO."""
    
    llm_passed = llm_judge_content(prompt, file_content)
    if llm_passed:
        results.append({"item": "文件格式与语义", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定文件格式专业，符合名册要求。"})
        total_score += 20
    else:
        results.append({"item": "文件格式与语义", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定文件中存在冗余对话、格式混乱或幻觉。"})

    # 输出最终结果
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
