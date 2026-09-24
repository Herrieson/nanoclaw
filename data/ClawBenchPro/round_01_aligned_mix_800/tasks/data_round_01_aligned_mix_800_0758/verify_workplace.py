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

def find_number_80(obj):
    """
    深度遍历 JSON 对象，严格匹配数字或字符串 '80' 
    (14 + 20 + 8 + 22 + 16 = 80)
    """
    if isinstance(obj, dict):
        return any(find_number_80(v) for v in obj.values())
    elif isinstance(obj, list):
        return any(find_number_80(v) for v in obj)
    elif isinstance(obj, (int, float)):
        return obj == 80 or obj == 80.0
    elif isinstance(obj, str):
        return obj.strip() == "80"
    return False

def check_no_hallucination(json_str):
    """
    通过底层原生代码对幻觉、杂音内容（个人绘画生活、小孩相关）进行无情打击
    """
    bad_words = ["easel", "crayon", "paint", "kids", "toddler", "diaper", "canvas"]
    lower_str = json_str.lower()
    for word in bad_words:
        if word in lower_str:
            return False, word
    return True, None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_file = os.path.join(workspace, "workplace_score.json")
    
    details = []
    total_score = 0
    target_path = os.path.join(workspace, "deliverables", "official_safety_report.json")
    
    # 1. 结构与路径检查 (10 分)
    if not os.path.exists(target_path):
        details.append({
            "item": "检查目标文件是否存在", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": f"文件 {target_path} 不存在"
        })
        with open(score_file, "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2, ensure_ascii=False)
        return
    else:
        details.append({
            "item": "检查目标文件是否存在", 
            "score": 10, 
            "max_score": 10, 
            "passed": True, 
            "reason": "目标文件正确存放于 deliverables 目录"
        })
        total_score += 10
        
    # 2. 确定性 JSON 解析检查 (10 分)
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)
        details.append({
            "item": "检查文件是否为合法 JSON", 
            "score": 10, 
            "max_score": 10, 
            "passed": True, 
            "reason": "成功将文件解析为 JSON 对象"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "检查文件是否为合法 JSON", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": f"解析 JSON 失败，非预期格式: {e}"
        })
        with open(score_file, "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return
        
    # 3. 结果精确度：总工时计算检测 (30 分)
    if find_number_80(data):
        details.append({
            "item": "计算本周工人们的总工时 (80小时)", 
            "score": 30, 
            "max_score": 30, 
            "passed": True, 
            "reason": "成功从 JSON 节点中提取并匹配到总工时 80"
        })
        total_score += 30
    else:
        details.append({
            "item": "计算本周工人们的总工时 (80小时)", 
            "score": 0, 
            "max_score": 30, 
            "passed": False, 
            "reason": "未能计算或记录正确的总工时 80 小时（或存放在错误的键值类型中）"
        })
        
    # 4. 严打幻觉：过滤私人生活数据 (20 分)
    is_clean, bad_word = check_no_hallucination(content)
    if is_clean:
        details.append({
            "item": "严格过滤私人生活与非建筑关联信息", 
            "score": 20, 
            "max_score": 20, 
            "passed": True, 
            "reason": "未发现画架、小孩等干扰性词汇，遵守了只记录真正建筑隐患的要求"
        })
        total_score += 20
    else:
        details.append({
            "item": "严格过滤私人生活与非建筑关联信息", 
            "score": 0, 
            "max_score": 20, 
            "passed": False, 
            "reason": f"未按要求过滤口述杂音，包含了与建筑无关的词汇: {bad_word}"
        })
        
    # 5. 非结构化语义检查：大模型鉴别真正的违规信息 (30 分)
    llm_prompt = """Does the provided JSON content correctly identify ALL FOUR of the following actual construction hazards? 
1. Scaffolding missing a guardrail.
2. Exposed wiring near main water line.
3. Subcontractors not wearing hard hats in overhead drop zone.
4. Unsecured trench over 5 feet deep.

It is OK if they are paraphrased, as long as the core meaning of these four specific construction hazards is present."""
    
    if llm_judge_content(llm_prompt, content):
         details.append({
             "item": "核心业务：包含全部 4 项真正的建筑安全隐患", 
             "score": 30, 
             "max_score": 30, 
             "passed": True, 
             "reason": "大模型判定内容中完整包含了 4 项真实建筑事故/隐患点"
         })
         total_score += 30
    else:
         details.append({
             "item": "核心业务：包含全部 4 项真正的建筑安全隐患", 
             "score": 0, 
             "max_score": 30, 
             "passed": False, 
             "reason": "大模型判定遗漏了某些隐患，或提取不够精确"
         })

    # 输出得分文件
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score, 
            "details": details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
