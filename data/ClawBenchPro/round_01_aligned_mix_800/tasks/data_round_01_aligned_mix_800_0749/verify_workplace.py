import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
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
    reports_dir = os.path.join(workspace, "reports")
    json_path = os.path.join(reports_dir, "missing_items.json")
    txt_path = os.path.join(reports_dir, "art_schools.txt")
    
    score_details = []
    total_score = 0
    
    # 1. Check reports directory
    if os.path.isdir(reports_dir):
        score_details.append({"item": "Reports目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "reports目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "Reports目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 reports 目录"})
        
    # 2. Check JSON file existence and schema
    json_data = None
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            score_details.append({"item": "missing_items.json 存在且格式合法", "score": 15, "max_score": 15, "passed": True, "reason": "文件存在且可被JSON解析"})
            total_score += 15
        except json.JSONDecodeError:
            score_details.append({"item": "missing_items.json 存在且格式合法", "score": 0, "max_score": 15, "passed": False, "reason": "文件存在但不符合JSON语法"})
    else:
        score_details.append({"item": "missing_items.json 存在且格式合法", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 missing_items.json"})

    # 3. Check JSON logic accuracy
    expected_missing = {
        "Oakridge Elementary": {"No. 2 Pencils (Box)": 10, "Blank Canvas": 2},
        "Cedar High": {"Backpacks": 5},
        "Maple Academy": {"Erasers": 10, "Rulers": 5}
    }
    
    if json_data is not None:
        if isinstance(json_data, dict):
            # 3.1 Check keys (No false positives like Pine View Middle)
            actual_keys = set(json_data.keys())
            expected_keys = set(expected_missing.keys())
            
            if "Pine View Middle" in actual_keys:
                score_details.append({"item": "正确剔除无短缺的学校", "score": 0, "max_score": 15, "passed": False, "reason": "包含了不该存在的 Pine View Middle"})
            elif actual_keys == expected_keys:
                score_details.append({"item": "正确识别存在短缺的学校", "score": 15, "max_score": 15, "passed": True, "reason": "学校名单完美匹配"})
                total_score += 15
            else:
                score_details.append({"item": "正确识别存在短缺的学校", "score": 5, "max_score": 15, "passed": False, "reason": f"学校名单不匹配，预期: {expected_keys}, 实际: {actual_keys}"})

            # 3.2 Check quantities strictly
            correct_qty = True
            hallucinations = False
            for school, items in expected_missing.items():
                if school in json_data:
                    actual_items = json_data[school]
                    if not isinstance(actual_items, dict):
                        correct_qty = False
                        continue
                    
                    for item, expected_qty in items.items():
                        if actual_items.get(item) != expected_qty:
                            correct_qty = False
                            
                    # check for hallucinated extra items
                    if len(actual_items) > len(items):
                        hallucinations = True
                else:
                    correct_qty = False
            
            if correct_qty and not hallucinations:
                score_details.append({"item": "精确提取短缺数量无捏造", "score": 30, "max_score": 30, "passed": True, "reason": "缺失物品计算严丝合缝，无多余捏造"})
                total_score += 30
            elif correct_qty and hallucinations:
                score_details.append({"item": "精确提取短缺数量无捏造", "score": 15, "max_score": 30, "passed": False, "reason": "核心数据计算正确，但存在多余的捏造字段"})
                total_score += 15
            else:
                score_details.append({"item": "精确提取短缺数量无捏造", "score": 0, "max_score": 30, "passed": False, "reason": "数量计算错误或遗漏了应该补足的物品"})
        else:
            score_details.append({"item": "JSON结构正确性", "score": 0, "max_score": 45, "passed": False, "reason": "JSON根节点必须是dict/object"})
    else:
        score_details.append({"item": "正确识别存在短缺的学校", "score": 0, "max_score": 15, "passed": False, "reason": "JSON文件缺失"})
        score_details.append({"item": "精确提取短缺数量无捏造", "score": 0, "max_score": 30, "passed": False, "reason": "JSON文件缺失"})

    # 4. Check TXT file using LLM (Non-structured semantic verification)
    if os.path.exists(txt_path):
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                txt_content = f.read()
            
            # Use LLM to verify if the note text is simple and contains ONLY the required schools
            prompt_text = (
                "The file should be a simple text list of schools that requested art supplies. "
                "It MUST clearly mention 'Oakridge Elementary' and 'Cedar High', and absolutely MUST NOT mention 'Pine View Middle' or 'Maple Academy'. "
                "It should be clean and not contain lengthy conversational filler."
            )
            is_valid = llm_judge_content(prompt_text, txt_content)
            
            if is_valid:
                score_details.append({"item": "艺术类学校TXT内容检查", "score": 30, "max_score": 30, "passed": True, "reason": "LLM验证通过：仅包含正确的学校名称，内容简洁"})
                total_score += 30
            else:
                score_details.append({"item": "艺术类学校TXT内容检查", "score": 10, "max_score": 30, "passed": False, "reason": "LLM验证失败：未包含指定学校、包含了错误学校、或存在太多冗余会话内容"})
                total_score += 10
        except Exception as e:
             score_details.append({"item": "艺术类学校TXT内容检查", "score": 0, "max_score": 30, "passed": False, "reason": f"读取TXT出错: {e}"})
    else:
        score_details.append({"item": "艺术类学校TXT内容检查", "score": 0, "max_score": 30, "passed": False, "reason": "未找到 art_schools.txt"})

    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
