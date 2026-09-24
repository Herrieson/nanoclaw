import os
import sys
import json
import httpx
from openai import OpenAI

# -----------------------------------------------------------------------------
# 配置与初始化
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# 预期数据定义 (基于任务脚本)
# -----------------------------------------------------------------------------
# RSVPs 解析结果：
# 1. Rosa (vegan)
# 2. Juan (none)
# 3. Miguel (peanut-allergy)
# 4. Elena (vegan, peanut-allergy)
# 5. Luis (none)
# 6. Blanca (dairy-free)
# 7. Chloe (dairy-free, vegan)
# 8. Mateo (none)
# Total: 8 guests
# Unique Restrictions: vegan, peanut-allergy, dairy-free

# 安全配方校验逻辑 (必须包含所有 restriction):
# Recipe 1: [peanut-allergy, vegetarian] -> 缺少 vegan, dairy-free (FAIL)
# Recipe 2: [vegan, peanut-allergy, dairy-free] -> 包含所有 (PASS)
# Recipe 3: [vegan, peanut-allergy, dairy-free, gluten-free] -> 包含所有 (PASS)
# Recipe 4: [dairy-free] -> 缺少 vegan, peanut-allergy (FAIL)

EXPECTED_TOTAL_GUESTS = 8
EXPECTED_RESTRICTIONS = {"vegan", "peanut-allergy", "dairy-free"}
EXPECTED_SAFE_RECIPES = ["Jackfruit Carnitas Tacos", "Mango Avocado Salad"]

# 计算购物清单 (Scale: 8 guests)
# Tacos (4 servings -> 8/4 = 2x): jackfruit: 4, tortillas: 16, onion: 2, cilantro: 1
# Salad (2 servings -> 8/2 = 4x): mango: 4, avocado: 4, lime: 4
EXPECTED_SHOPPING_LIST = {
    "jackfruit (cans)": 4,
    "tortillas": 16,
    "onion": 2,
    "cilantro (bunch)": 1,
    "mango": 4,
    "avocado": 4,
    "lime": 4
}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    summary_path = os.path.join(workspace, "deliverables/summary.json")
    
    score = 0
    details = []

    # 1. 文件存在性检查 (10分)
    if os.path.exists(summary_path):
        score += 10
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables/summary.json 已生成"})
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        # 写入最终结果并退出
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # 2. 内容解析与基础结构检查 (10分)
    try:
        with open(summary_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score += 10
        details.append({"item": "JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功且结构完整"})
    except Exception as e:
        details.append({"item": "JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # 3. 总人数验证 (20分)
    actual_guests = data.get("total_guests")
    if actual_guests == EXPECTED_TOTAL_GUESTS:
        score += 20
        details.append({"item": "总人数统计", "score": 20, "max_score": 20, "passed": True, "reason": f"人数正确: {actual_guests}"})
    else:
        details.append({"item": "总人数统计", "score": 0, "max_score": 20, "passed": False, "reason": f"期望 {EXPECTED_TOTAL_GUESTS}, 实际 {actual_guests}"})

    # 4. 饮食限制集合验证 (15分)
    actual_restrictions = set(data.get("restrictions", []))
    if actual_restrictions == EXPECTED_RESTRICTIONS:
        score += 15
        details.append({"item": "饮食限制提取", "score": 15, "max_score": 15, "passed": True, "reason": "所有饮食限制标签匹配成功"})
    else:
        details.append({"item": "饮食限制提取", "score": 0, "max_score": 15, "passed": False, "reason": f"不匹配。期望: {EXPECTED_RESTRICTIONS}, 实际: {actual_restrictions}"})

    # 5. 安全配方筛选逻辑 (25分)
    actual_recipes = data.get("safe_recipes", [])
    if set(actual_recipes) == set(EXPECTED_SAFE_RECIPES):
        score += 25
        details.append({"item": "安全配方筛选", "score": 25, "max_score": 25, "passed": True, "reason": "正确筛选出完全满足所有限制的配方"})
    else:
        details.append({"item": "安全配方筛选", "score": 0, "max_score": 25, "passed": False, "reason": f"筛选错误。应选: {EXPECTED_SAFE_RECIPES}, 实际: {actual_recipes}"})

    # 6. 购物清单计算 (20分)
    actual_shopping = data.get("shopping_list", {})
    math_error = False
    for item, qty in EXPECTED_SHOPPING_LIST.items():
        if actual_shopping.get(item) != qty:
            math_error = True
            break
    
    if not math_error and len(actual_shopping) == len(EXPECTED_SHOPPING_LIST):
        score += 20
        details.append({"item": "购物清单数学计算", "score": 20, "max_score": 20, "passed": True, "reason": "配方按人数缩放计算精准"})
    else:
        # 使用 LLM 检查是否存在单位换算导致的微小差异或语义一致性
        prompt = f"The expected shopping list is {EXPECTED_SHOPPING_LIST}. Does the agent's list contain the same items and quantities (ignoring minor phrasing)?"
        if llm_judge_content(prompt, json.dumps(actual_shopping)):
            score += 15
            details.append({"item": "购物清单数学计算", "score": 15, "max_score": 20, "passed": True, "reason": "数学基本正确，可能存在细微格式差异"})
        else:
            details.append({"item": "购物清单数学计算", "score": 0, "max_score": 20, "passed": False, "reason": "购物清单计算错误或条目不符"})

    # 写入最终得分
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(score), "details": details}, f)

if __name__ == "__main__":
    main()
