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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    target_dir = os.path.join(workspace, "kitchen_prep")
    target_file = os.path.join(target_dir, "winning_recipe_order.json")
    
    # 1. 检查目标目录 (10分)
    if os.path.isdir(target_dir):
        total_score += 10
        score_details.append({"item": "检查目标目录 kitchen_prep", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
    else:
        score_details.append({"item": "检查目标目录 kitchen_prep", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        
    # 2. 检查输出文件是否存在 (20分)
    if os.path.isfile(target_file):
        total_score += 20
        score_details.append({"item": "检查文件 winning_recipe_order.json", "score": 20, "max_score": 20, "passed": True, "reason": "文件存在"})
        
        # 解析 JSON 格式
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content_str = f.read()
                data = json.loads(content_str)
                
            total_score += 10
            score_details.append({"item": "JSON 格式解析", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON"})
            
            # 3. 检查字段完整性与多余字段 (20分)
            required_keys = {"recipe_name", "total_cost", "total_carbon_footprint", "ingredients"}
            actual_keys = set(data.keys())
            
            if required_keys.issubset(actual_keys):
                if len(actual_keys) == len(required_keys):
                    total_score += 20
                    score_details.append({"item": "JSON 字段完整性", "score": 20, "max_score": 20, "passed": True, "reason": "包含所有必填字段且无冗余捏造字段"})
                else:
                    total_score += 5
                    score_details.append({"item": "JSON 字段完整性", "score": 5, "max_score": 20, "passed": False, "reason": f"包含必需字段，但存在幻觉或捏造的多余字段: {actual_keys - required_keys}"})
            else:
                score_details.append({"item": "JSON 字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": f"缺失必需字段: {required_keys - actual_keys}"})
            
            # 4. 检查确定性关联逻辑 (20分)
            valid_recipes = ["Traditional_Lechon", "Eco_Plantain_Bowl", "Fancy_Seafood_Paella", "Chicken_Mojo"]
            recipe_name = data.get("recipe_name", "")
            if recipe_name in valid_recipes:
                total_score += 10
                score_details.append({"item": "菜谱名称合法性", "score": 10, "max_score": 10, "passed": True, "reason": f"菜谱名 {recipe_name} 合法"})
                
                # 检查食材列表是否与菜谱对应 (简单检查非空及类型)
                ingredients = data.get("ingredients")
                if isinstance(ingredients, list) and len(ingredients) > 0:
                    total_score += 10
                    score_details.append({"item": "食材列表结构", "score": 10, "max_score": 10, "passed": True, "reason": "食材列表为有效的数组结构"})
                else:
                    score_details.append({"item": "食材列表结构", "score": 0, "max_score": 10, "passed": False, "reason": "食材列表为空或类型错误"})
            else:
                score_details.append({"item": "菜谱名称合法性", "score": 0, "max_score": 10, "passed": False, "reason": "菜谱名称不在候选列表中"})
                score_details.append({"item": "食材列表结构", "score": 0, "max_score": 10, "passed": False, "reason": "由于菜谱名称错误，跳过匹配检查"})
                
            # 5. LLM 检测幻觉与附加说明 (20分)
            # 尽管是 JSON，使用 LLM 判断其中是否夹带了废话或者非专业词汇
            prompt = "Please check if the following JSON contains ONLY factual, direct culinary data. Return 'NO' if it contains conversational filler, extra hallucinated keys like 'notes' with chatty text, or markdown code blocks outside the JSON structure. Return 'YES' if it is strictly clean."
            is_clean = llm_judge_content(prompt, content_str)
            if is_clean:
                total_score += 20
                score_details.append({"item": "大模型语义纯净度检测", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定输出没有任何非业务的闲聊和幻觉注入"})
            else:
                score_details.append({"item": "大模型语义纯净度检测", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定文件中包含了不必要的闲聊、解释性废话或幻觉内容"})

        except json.JSONDecodeError:
            score_details.append({"item": "JSON 格式解析", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 解析失败"})
            score_details.append({"item": "JSON 字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": "前置依赖失败"})
            score_details.append({"item": "菜谱名称合法性", "score": 0, "max_score": 10, "passed": False, "reason": "前置依赖失败"})
            score_details.append({"item": "食材列表结构", "score": 0, "max_score": 10, "passed": False, "reason": "前置依赖失败"})
            score_details.append({"item": "大模型语义纯净度检测", "score": 0, "max_score": 20, "passed": False, "reason": "前置依赖失败"})
    else:
        score_details.append({"item": "检查文件 winning_recipe_order.json", "score": 0, "max_score": 20, "passed": False, "reason": "目标文件未生成"})
        score_details.extend([
            {"item": "JSON 格式解析", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"},
            {"item": "JSON 字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"},
            {"item": "菜谱名称合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"},
            {"item": "食材列表结构", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"},
            {"item": "大模型语义纯净度检测", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"}
        ])

    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
