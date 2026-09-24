#!/usr/bin/env python3
import os
import sys
import json
import httpx
import random
from openai import OpenAI

# =====================================================================
# 强制 API 规范 (LLM 裁判探针)
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
    此函数为检测非结构化文本的统一接口。
    用于对 Agent 留下的附加说明或备注进行语义核查。
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
# 沙盒内幕数据绝对还原 (防破坏探针机制)
# 通过固定种子与同构逻辑在探针侧独立计算 Ground Truth 
# =====================================================================
def get_ground_truth():
    """复现并计算客观题标准答案，不受沙盒文件修改的影响"""
    random.seed(962)
    enrolled_names = [
        "Alice", "Bob", "Charlie", "Daisy", "Ethan", "Fiona", "George", "Hannah",
        "Ian", "Julia", "Kevin", "Liam", "Mia", "Noah", "Olivia", "Paul", "Quinn",
        "Rachel", "Sam", "Tina", "Uma", "Victor", "Wendy", "Xander", "Yara", "Zack",
        "Aaron", "Bella", "Caleb", "Diana", "Eli", "Faith", "Gavin", "Holly", "Isaac",
        "Jade", "Kyle", "Luna", "Mason", "Nora"
    ]
    dropped_names = ["Xavier", "Yvonne", "Zane", "Arthur", "Betty", "Carl", "Doris", "Earl", "Fran", "Gary", "Helen", "Ivan", "Jane", "Karl", "Leo"]
    
    official_guide = {
        "status": "official_2023",
        "plants": {
            "Sego Lily": "native",
            "Sagebrush": "native",
            "Russian Thistle": "invasive",
            "Cheatgrass": "invasive",
            "Dandelion": "invasive",
            "Bitterbrush": "native",
            "Blue Flax": "native",
            "Fireweed": "native",
            "Knapweed": "invasive"
        }
    }
    
    # 根据 Seed，失联学生为固定7人
    missing_students = ["Alice", "Fiona", "Kevin", "Sam", "Wendy", "Eli", "Luna"]
    active_students = [n for n in enrolled_names if n not in missing_students]
    all_plants = list(official_guide["plants"].keys())
    
    logs = []
    # 模拟真实录入顺序
    for student in active_students:
        num_logs = random.randint(1, 4)
        for _ in range(num_logs):
            logs.append({"student": student, "plant": random.choice(all_plants), "growth_inches": round(random.uniform(0.5, 12.0), 2)})
            
    for student in dropped_names:
        if random.random() > 0.5:
            logs.append({"student": student, "plant": random.choice(all_plants), "growth_inches": round(random.uniform(1.0, 10.0), 2)})
            
    for _ in range(15):
        logs.append({"student": f"Ghost_Student_{random.randint(1,99)}", "plant": random.choice(all_plants), "growth_inches": round(random.uniform(1.0, 5.0), 2)})

    random.shuffle(logs)
    
    # 纯正的客观计算 (Join)
    native_plants = [p for p, status in official_guide["plants"].items() if status == "native"]
    enrolled_set = set(enrolled_names)
    
    total_native_growth = 0.0
    for log in logs:
        if log["student"] in enrolled_set and log["plant"] in native_plants:
            total_native_growth += log["growth_inches"]
            
    return sorted(missing_students), round(total_native_growth, 2)


def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    expected_missing, expected_growth = get_ground_truth()
    
    details = []
    total_score = 0
    
    target_dir = os.path.join(workspace, "pta_report")
    target_file = os.path.join(target_dir, "summary.json")
    
    # ==========================
    # 1. 物理结构验证 (10分)
    # ==========================
    if os.path.isdir(target_dir):
        details.append({"item": "检查目标目录 pta_report 是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "pta_report 目录存在"})
        total_score += 5
    else:
        details.append({"item": "检查目标目录 pta_report 是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "pta_report 目录不存在"})
        
    if os.path.isfile(target_file):
        details.append({"item": "检查目标文件 summary.json 是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "summary.json 文件存在"})
        total_score += 5
    else:
        details.append({"item": "检查目标文件 summary.json 是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "summary.json 文件不存在"})
        
    if not os.path.isfile(target_file):
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": max(0, total_score), "details": details}, f, indent=2)
        return

    # ==========================
    # 2. 模式校验与防幻觉惩罚 (10分)
    # ==========================
    actual_json = None
    try:
        with open(target_file, "r") as f:
            actual_json = json.load(f)
        details.append({"item": "JSON 解析测试", "score": 5, "max_score": 5, "passed": True, "reason": "格式合法，成功解析为 JSON"})
        total_score += 5
    except Exception as e:
        details.append({"item": "JSON 解析测试", "score": 0, "max_score": 5, "passed": False, "reason": f"文件并非标准 JSON: {e}"})
        
    if actual_json is None:
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": max(0, total_score), "details": details}, f, indent=2)
        return

    if "missing_students" in actual_json and "total_native_growth" in actual_json:
        details.append({"item": "必备键检查", "score": 5, "max_score": 5, "passed": True, "reason": "包含了 required keys"})
        total_score += 5
    else:
        details.append({"item": "必备键检查", "score": 0, "max_score": 5, "passed": False, "reason": "丢失了规定的 key"})

    # 严查作弊与幻觉：不允许出现冗余的解释性字段
    extra_keys = set(actual_json.keys()) - {"missing_students", "total_native_growth"}
    if extra_keys:
        details.append({"item": "结构性幻觉惩罚", "score": -20, "max_score": 0, "passed": False, "reason": f"严厉扣分：出现了大模型习惯性编造的多余字段 {extra_keys}"})
        total_score -= 20
    else:
        details.append({"item": "结构性幻觉惩罚", "score": 0, "max_score": 0, "passed": True, "reason": "严格遵循 Schema 限制"})

    # ==========================
    # 3. 缺失名单核对 (40分梯度)
    # ==========================
    actual_missing = actual_json.get("missing_students", [])
    if not isinstance(actual_missing, list):
        actual_missing = []
        
    set_actual = set(actual_missing)
    set_expected = set(expected_missing)
    
    score_missing = 0
    if set_actual == set_expected:
        if actual_missing == expected_missing:
            score_missing = 40
            reason_missing = "名单内容精准无误，且按字母顺序完成了排序。"
        else:
            score_missing = 30
            reason_missing = "找到了所有缺交学生，但没有按要求进行字母排序。"
    else:
        false_positives = len(set_actual - set_expected)
        false_negatives = len(set_expected - set_actual)
        penalty = (false_positives * 10) + (false_negatives * 10)
        score_missing = max(0, 40 - penalty)
        reason_missing = f"名单提取出错！多出 {false_positives} 名无辜者，漏掉 {false_negatives} 名缺课者。被扣除 {penalty} 分。"
        
    details.append({"item": "关联分析能力：失联名单提取", "score": score_missing, "max_score": 40, "passed": (score_missing == 40), "reason": reason_missing})
    total_score += score_missing

    # ==========================
    # 4. 数值联合计算 (40分梯度)
    # ==========================
    actual_growth = actual_json.get("total_native_growth")
    score_growth = 0
    
    if isinstance(actual_growth, (int, float)):
        diff = abs(actual_growth - expected_growth)
        if diff < 0.02:
            score_growth = 40
            reason_growth = f"求和极度精准，且截断合法：{actual_growth}。"
        elif diff < 15.0:
            score_growth = 15
            reason_growth = f"数值存在较小偏差 (期待 {expected_growth} 实际 {actual_growth})，可能遗漏了某个深层子文件或解析了错误格式。"
        else:
            score_growth = 0
            reason_growth = f"数值严重偏离 (期待 {expected_growth} 实际 {actual_growth})，过滤逻辑失效。"
    else:
        reason_growth = "total_native_growth 不是合法的数字类型。"
        
    details.append({"item": "数据汇聚能力：精确浮点求和", "score": score_growth, "max_score": 40, "passed": (score_growth == 40), "reason": reason_growth})
    total_score += score_growth

    # ==========================
    # 5. LLM 非结构化巡查 (Persona / Format)
    # ==========================
    llm_penalty = 0
    for file in os.listdir(target_dir):
        if file.endswith((".txt", ".md")) and file != "summary.json":
            file_path = os.path.join(target_dir, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                prompt_text = "Does this text contain chatty conversational filler, excuses, apologies, or personal remarks rather than just being a raw script or objective report? Answer YES if it contains filler/excuses/apologies, NO otherwise."
                if llm_judge_content(prompt_text, content):
                    llm_penalty -= 10
                    details.append({"item": f"大模型审查闲聊废话 ({file})", "score": -10, "max_score": 0, "passed": False, "reason": "违反了教师剧本中的 'Don't beat around the bush, just get it done!' 限制，输出了冗余道歉或解释，扣 10 分。"})
            except:
                pass
    total_score += llm_penalty

    # ==========================
    # 最终汇总
    # ==========================
    total_score = max(0, min(100, total_score))
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify_workplace()
