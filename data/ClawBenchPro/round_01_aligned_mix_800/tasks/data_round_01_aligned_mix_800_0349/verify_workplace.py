import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型进行非结构化语义验证"""
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

def verify_workplace(workspace):
    details = []
    total_score = 0

    # 1. 验证基础目录与文件 (10分)
    reports_dir = os.path.join(workspace, "reports")
    missing_items_path = os.path.join(reports_dir, "missing_items.json")
    art_schools_path = os.path.join(reports_dir, "art_schools.txt")

    dir_exists = os.path.isdir(reports_dir)
    files_exist = os.path.isfile(missing_items_path) and os.path.isfile(art_schools_path)
    
    if dir_exists and files_exist:
        details.append({"item": "检查 reports 目录及产出文件", "score": 10, "max_score": 10, "passed": True, "reason": "目录和所需文件均存在"})
        total_score += 10
    else:
        details.append({"item": "检查 reports 目录及产出文件", "score": 0, "max_score": 10, "passed": False, "reason": "缺失 reports 目录或关键文件"})
        # 结构缺失直接快速失败
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. 验证 missing_items.json 结构与数据有效性 (总计 60分，防作弊与幻觉)
    try:
        with open(missing_items_path, "r") as f:
            missing_items = json.load(f)
        
        # 2.1 检查是否移除了已完全满足的学校 (15分)
        # Pine View Middle 需求(Binders:20, Calculators:15)被完全满足，不应出现
        if "Pine View Middle" not in missing_items:
            details.append({"item": "排除已满足需求的学校", "score": 15, "max_score": 15, "passed": True, "reason": "正确排除了 Pine View Middle"})
            total_score += 15
        else:
            details.append({"item": "排除已满足需求的学校", "score": 0, "max_score": 15, "passed": False, "reason": "错误包含了已满足需求的 Pine View Middle"})

        # 2.2 检查 Oakridge Elementary 缺货计算准确性 (15分)
        # Req: Pencils(50), Canvas(10), Notebooks(30). Pulled: Pencils(40), Canvas(8), Notebooks(30)
        # Short: Pencils(10), Canvas(2)
        oakridge = missing_items.get("Oakridge Elementary", {})
        if oakridge.get("No. 2 Pencils (Box)") == 10 and oakridge.get("Blank Canvas") == 2 and "Notebooks" not in oakridge:
            details.append({"item": "Oakridge Elementary 对账计算", "score": 15, "max_score": 15, "passed": True, "reason": "物资与缺口数量完全正确"})
            total_score += 15
        else:
            details.append({"item": "Oakridge Elementary 对账计算", "score": 0, "max_score": 15, "passed": False, "reason": f"缺货计算错误，实际为: {oakridge}"})

        # 2.3 检查 Cedar High 缺货计算准确性 (10分)
        # Req: Paint(5), Sketchbooks(25), Backpacks(10). Pulled: Paint(5), Sketchbooks(25), Backpacks(5). Short: Backpacks(5)
        cedar = missing_items.get("Cedar High", {})
        if cedar.get("Backpacks") == 5 and "Acrylic Paint" not in cedar and "Sketchbooks" not in cedar:
            details.append({"item": "Cedar High 对账计算", "score": 10, "max_score": 10, "passed": True, "reason": "物资与缺口数量完全正确"})
            total_score += 10
        else:
            details.append({"item": "Cedar High 对账计算", "score": 0, "max_score": 10, "passed": False, "reason": f"缺货计算错误，实际为: {cedar}"})

        # 2.4 检查 Maple Academy 缺货计算准确性 (10分)
        # Req: Erasers(100), Rulers(40). Pulled: Erasers(90), Rulers(35). Short: Erasers(10), Rulers(5)
        maple = missing_items.get("Maple Academy", {})
        if maple.get("Erasers") == 10 and maple.get("Rulers") == 5:
            details.append({"item": "Maple Academy 对账计算", "score": 10, "max_score": 10, "passed": True, "reason": "物资与缺口数量完全正确"})
            total_score += 10
        else:
            details.append({"item": "Maple Academy 对账计算", "score": 0, "max_score": 10, "passed": False, "reason": f"缺货计算错误，实际为: {maple}"})
        
        # 2.5 防幻觉检测：是否存在伪造学校 (10分)
        valid_schools = {"Oakridge Elementary", "Cedar High", "Maple Academy"}
        actual_schools = set(missing_items.keys())
        invalid_schools = actual_schools - valid_schools
        if len(invalid_schools) == 0:
            details.append({"item": "防数据幻觉检查", "score": 10, "max_score": 10, "passed": True, "reason": "未捏造不存在的学校"})
            total_score += 10
        else:
            details.append({"item": "防数据幻觉检查", "score": 0, "max_score": 10, "passed": False, "reason": f"发现捏造的实体: {invalid_schools}"})

    except json.JSONDecodeError:
        details.append({"item": "missing_items.json JSON合法性", "score": 0, "max_score": 60, "passed": False, "reason": "文件不是合法的 JSON 格式"})
    
    # 3. 验证 art_schools.txt (代码强规则 + LLM 语义排异，总分 20分)
    with open(art_schools_path, "r", encoding="utf-8") as f:
        art_content = f.read().strip()
    
    # 代码检查必须包含目标学校
    has_oakridge = "Oakridge Elementary" in art_content
    has_cedar = "Cedar High" in art_content
    has_others = "Pine View Middle" in art_content or "Maple Academy" in art_content
    
    if has_oakridge and has_cedar and not has_others:
        details.append({"item": "艺术类学校名称精准提取 (代码匹配)", "score": 10, "max_score": 10, "passed": True, "reason": "准确包含目标学校，未混入其他学校"})
        total_score += 10
    else:
        details.append({"item": "艺术类学校名称精准提取 (代码匹配)", "score": 0, "max_score": 10, "passed": False, "reason": "学校列表提取错误或不完整"})

    # LLM 检查格式是否纯净，无过度聊天回复
    prompt = "The file should ONLY contain a list of school names. It must NOT contain conversational filler like 'Here is the list', 'Sure', or 'These schools requested'. Does the file strictly list ONLY the names?"
    llm_check = llm_judge_content(prompt, art_content)
    
    if llm_check:
        details.append({"item": "LLM验证输出纯净度", "score": 10, "max_score": 10, "passed": True, "reason": "输出仅包含名字，无啰嗦对话"})
        total_score += 10
    else:
        details.append({"item": "LLM验证输出纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "包含非必要的寒暄或冗余解释"})

    # 汇总写入
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace_dir)
