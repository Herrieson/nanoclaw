import os
import sys
import json
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
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []
    
    target_dir = os.path.join(workspace, "parent_reports")
    target_file = os.path.join(target_dir, "safe_garden_snacks.json")
    
    # 1. 检查目录 (10分)
    if os.path.isdir(target_dir):
        total_score += 10
        details.append({"item": "检查目标目录 parent_reports 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已创建"})
    else:
        details.append({"item": "检查目标目录 parent_reports 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        
    # 2. 检查文件及 JSON 格式 (20分)
    json_data = None
    if os.path.isfile(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            if isinstance(json_data, dict):
                total_score += 20
                details.append({"item": "检查目标文件是否存在且为合法字典JSON", "score": 20, "max_score": 20, "passed": True, "reason": "JSON格式合法且为字典"})
            else:
                details.append({"item": "检查目标文件是否存在且为合法字典JSON", "score": 10, "max_score": 20, "passed": False, "reason": "文件是合法的JSON但顶层不是字典"})
        except Exception as e:
            details.append({"item": "检查目标文件是否存在且为合法字典JSON", "score": 5, "max_score": 20, "passed": False, "reason": f"文件存在但无法被解析为JSON: {e}"})
    else:
        details.append({"item": "检查目标文件是否存在且为合法字典JSON", "score": 0, "max_score": 20, "passed": False, "reason": "文件 safe_garden_snacks.json 不存在"})
        
    if isinstance(json_data, dict):
        # 3. 验证 Noah 的结果 (20分)
        # 条件：有过敏 (Peanuts)，有 garden time。零食：celery sticks
        noah_snack = json_data.get("Noah")
        if noah_snack:
            prompt = "Does the following snack description strictly mention or mean 'celery sticks' and NOTHING contradictory?"
            if llm_judge_content(prompt, noah_snack):
                total_score += 20
                details.append({"item": "验证 Noah 是否被正确提取及其零食", "score": 20, "max_score": 20, "passed": True, "reason": f"成功提取了 Noah 的零食: {noah_snack}"})
            else:
                total_score += 10
                details.append({"item": "验证 Noah 是否被正确提取及其零食", "score": 10, "max_score": 20, "passed": False, "reason": f"Noah 提取了但零食语义不符: {noah_snack}"})
        else:
            details.append({"item": "验证 Noah 是否被正确提取及其零食", "score": 0, "max_score": 20, "passed": False, "reason": "缺少 Noah 这一项"})
            
        # 4. 验证 Chloe 的结果 (20分)
        # 条件：有过敏 (Gluten)，有 garden time ("redding up the garden tools")。零食：carrot sticks
        chloe_snack = json_data.get("Chloe")
        if chloe_snack:
            prompt = "Does the following snack description strictly mention or mean 'carrot sticks' and NOTHING contradictory?"
            if llm_judge_content(prompt, chloe_snack):
                total_score += 20
                details.append({"item": "验证 Chloe 是否被正确提取及其零食", "score": 20, "max_score": 20, "passed": True, "reason": f"成功提取了 Chloe 的零食: {chloe_snack}"})
            else:
                total_score += 10
                details.append({"item": "验证 Chloe 是否被正确提取及其零食", "score": 10, "max_score": 20, "passed": False, "reason": f"Chloe 提取了但零食语义不符: {chloe_snack}"})
        else:
            details.append({"item": "验证 Chloe 是否被正确提取及其零食", "score": 0, "max_score": 20, "passed": False, "reason": "缺少 Chloe 这一项"})
            
        # 5. 验证是否剔除了干扰项 Emma, Liam, Mason (30分)
        # Emma: 有 garden time，但没有过敏 (None) -> 应被剔除
        # Liam: 有过敏 (Dairy)，但没有 garden time (stayed inside) -> 应被剔除
        # Mason: 有过敏 (Shellfish)，但没有 garden time (napping) -> 应被剔除
        false_positives = [name for name in ["Emma", "Liam", "Mason"] if name in json_data]
        other_extras = [name for name in json_data.keys() if name not in ["Noah", "Chloe", "Emma", "Liam", "Mason"]]
        
        if not false_positives and not other_extras:
            total_score += 30
            details.append({"item": "验证是否严格剔除不符合交叉条件的儿童及捏造数据", "score": 30, "max_score": 30, "passed": True, "reason": "没有任何错误数据或幻觉"})
        else:
            penalty_score = max(0, 30 - 15 * (len(false_positives) + len(other_extras)))
            total_score += penalty_score
            details.append({"item": "验证是否严格剔除不符合交叉条件的儿童及捏造数据", "score": penalty_score, "max_score": 30, "passed": False, "reason": f"混入了错误或幻觉节点: {false_positives + other_extras}"})
            
    else:
        # 如果不是字典，跳过3-5项
        details.append({"item": "验证 Noah 是否被正确提取及其零食", "score": 0, "max_score": 20, "passed": False, "reason": "JSON不是字典，无法验证键值对"})
        details.append({"item": "验证 Chloe 是否被正确提取及其零食", "score": 0, "max_score": 20, "passed": False, "reason": "JSON不是字典，无法验证键值对"})
        details.append({"item": "验证是否严格剔除不符合交叉条件的儿童及捏造数据", "score": 0, "max_score": 30, "passed": False, "reason": "JSON不是字典，无法验证键值对"})

    score_report = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_report, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
