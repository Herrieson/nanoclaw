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
    """
    非结构化语义验证统一接口，依赖 LLM
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

def check_value_in_json(data, target_type, target_val):
    """
    原生代码确定性解析：健壮地在嵌套的 JSON 中查找指定类型的数值。
    应对 Agent 可能将其表示为 int, float 甚至 string 的情况。
    """
    found = False
    def traverse(obj):
        nonlocal found
        if isinstance(obj, dict):
            for v in obj.values():
                traverse(v)
        elif isinstance(obj, list):
            for item in obj:
                traverse(item)
        elif isinstance(obj, (int, float)):
            if target_type == 'count' and obj == target_val:
                found = True
            elif target_type == 'avg' and abs(obj - target_val) < 0.01:
                found = True
        elif isinstance(obj, str):
            try:
                num = float(obj)
                if target_type == 'count' and int(num) == target_val and num == int(num):
                    found = True
                elif target_type == 'avg' and abs(num - target_val) < 0.01:
                    found = True
            except ValueError:
                pass
    traverse(data)
    return found

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    json_path = os.path.join(deliverables_dir, "clean_results.json")
    
    total_score = 0
    details = []

    # 1. 结构化目录检查 (10 分)
    if os.path.isdir(deliverables_dir):
        details.append({"item": "检查 deliverables 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables 目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录不存在"})
        
    # 2. 结构化文件检查 (10 分)
    if os.path.isfile(json_path):
        details.append({"item": "检查 clean_results.json 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件存在"})
        total_score += 10
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content_text = f.read()
            data = json.loads(content_text)
            
            # 3. 结构合法性解析 (10 分)
            details.append({"item": "检查 JSON 文件格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式完全合法"})
            total_score += 10
            
            # 4. 精准数值提取：有效样本数量 = 4 (20 分)
            has_count = check_value_in_json(data, 'count', 4)
            if has_count:
                details.append({"item": "精准验证：有效样本数量是否为 4", "score": 20, "max_score": 20, "passed": True, "reason": "成功在 JSON 中匹配到计算正确的样本数量 (4)"})
                total_score += 20
            else:
                details.append({"item": "精准验证：有效样本数量是否为 4", "score": 0, "max_score": 20, "passed": False, "reason": "未在 JSON 的 values 中找到正确的数量 4，计算错误或幻觉捏造"})
                
            # 5. 精准数值提取：平均值 = 300.25 (30 分)
            has_avg = check_value_in_json(data, 'avg', 300.25)
            if has_avg:
                details.append({"item": "精准验证：平均值是否为 300.25", "score": 30, "max_score": 30, "passed": True, "reason": "成功在 JSON 中匹配到计算正确的平均值 (300.25)"})
                total_score += 30
            else:
                details.append({"item": "精准验证：平均值是否为 300.25", "score": 0, "max_score": 30, "passed": False, "reason": "未在 JSON 的 values 中找到正确的平均值 300.25，计算错误或幻觉捏造"})
                
            # 6. 语义检查：JSON Key 合理性 (20 分)
            llm_prompt = "Examine the keys in this JSON object. Do the keys logically and reasonably represent the semantic concepts of 'valid sample count' and 'average value of valid samples'? Answer YES if the keys match these concepts and contain no irrelevant hallucinated information."
            is_semantic_ok = llm_judge_content(llm_prompt, content_text)
            if is_semantic_ok:
                details.append({"item": "利用大模型检查 JSON 键名语义合理性", "score": 20, "max_score": 20, "passed": True, "reason": "键名语义合理，符合业务场景"})
                total_score += 20
            else:
                details.append({"item": "利用大模型检查 JSON 键名语义合理性", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定键名语义含糊或包含无关的幻觉字段"})
                
        except json.JSONDecodeError:
            details.append({"item": "检查 JSON 文件格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 解析失败，文件格式损毁"})
            details.append({"item": "精准验证：有效样本数量", "score": 0, "max_score": 20, "passed": False, "reason": "前置条件失败跳过"})
            details.append({"item": "精准验证：平均值", "score": 0, "max_score": 30, "passed": False, "reason": "前置条件失败跳过"})
            details.append({"item": "利用大模型检查 JSON 键名语义合理性", "score": 0, "max_score": 20, "passed": False, "reason": "前置条件失败跳过"})
    else:
        details.append({"item": "检查 clean_results.json 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 JSON 文件"})
        details.append({"item": "检查 JSON 文件格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        details.append({"item": "精准验证：有效样本数量", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        details.append({"item": "精准验证：平均值", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})
        details.append({"item": "利用大模型检查 JSON 键名语义合理性", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
