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

def check_pair_exists(obj, name, color):
    """
    递归搜索自定义 JSON 结构，验证是否 name 和 color 成对出现。
    允许的成对形式：
    1. {"Frostbite Sword": "#00FFFF"}
    2. {"name": "Frostbite Sword", "color": "#00FFFF"}
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).strip() == name and str(v).strip() == color:
                return True
            if str(k).strip() == color and str(v).strip() == name:
                return True
        vals = [str(v).strip() for v in obj.values()]
        if name in vals and color in vals:
            return True
        for v in obj.values():
            if check_pair_exists(v, name, color):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if check_pair_exists(item, name, color):
                return True
    return False

def check_junk_data(obj):
    """
    展平 JSON，确保没有混入其它作者、普通品质或不该出现的数据。
    """
    junk_keywords = ["SomeGuy_88", "Lame Axe", "Common", "Basic Boots", "AUTHOR=WiscArt99"]
    all_strings = []
    
    def extract_strings(o):
        if isinstance(o, dict):
            for k, v in o.items():
                all_strings.append(str(k))
                extract_strings(v)
        elif isinstance(o, list):
            for item in o:
                extract_strings(item)
        else:
            if o is not None:
                all_strings.append(str(o))
                
    extract_strings(obj)
    
    for s in all_strings:
        for jk in junk_keywords:
            if jk.lower() in s.lower():
                return False, f"Found extraneous/junk data: {jk}"
    return True, "No junk data found."

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    target_dir = os.path.join(workspace, "fixed_assets")
    target_file = os.path.join(target_dir, "my_mod_pack.json")
    
    # 1. Check Directory
    if os.path.isdir(target_dir):
        total_score += 10
        score_details.append({"item": "检查目标目录 fixed_assets 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
    else:
        score_details.append({"item": "检查目标目录 fixed_assets 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        
    # 2. Check File
    file_exists = os.path.isfile(target_file)
    if file_exists:
        total_score += 10
        score_details.append({"item": "检查 my_mod_pack.json 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    else:
        score_details.append({"item": "检查 my_mod_pack.json 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        
    # 3 & 4 & 5. Check JSON Content
    if file_exists:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            total_score += 20
            score_details.append({"item": "验证 JSON 格式合法性", "score": 20, "max_score": 20, "passed": True, "reason": "成功解析为合法 JSON"})
            
            # Target 1: Frostbite Sword
            if check_pair_exists(data, "Frostbite Sword", "#00FFFF"):
                total_score += 15
                score_details.append({"item": "提取目标 1 (Frostbite Sword)", "score": 15, "max_score": 15, "passed": True, "reason": "成功提取名称与颜色"})
            else:
                score_details.append({"item": "提取目标 1 (Frostbite Sword)", "score": 0, "max_score": 15, "passed": False, "reason": "未找到或数据不匹配"})
                
            # Target 2: Cheese Crown (from .tmp)
            if check_pair_exists(data, "Cheese Crown", "#FFD700"):
                total_score += 15
                score_details.append({"item": "提取目标 2 (Cheese Crown)", "score": 15, "max_score": 15, "passed": True, "reason": "成功从非常规后缀文件提取"})
            else:
                score_details.append({"item": "提取目标 2 (Cheese Crown)", "score": 0, "max_score": 15, "passed": False, "reason": "未找到或数据不匹配"})
                
            # Target 3: Cranberry Potion (from .txt)
            if check_pair_exists(data, "Cranberry Potion", "#AA0033"):
                total_score += 15
                score_details.append({"item": "提取目标 3 (Cranberry Potion)", "score": 15, "max_score": 15, "passed": True, "reason": "成功从非常规后缀文件提取"})
            else:
                score_details.append({"item": "提取目标 3 (Cranberry Potion)", "score": 0, "max_score": 15, "passed": False, "reason": "未找到或数据不匹配"})
                
            # Junk Data / Pureness
            is_pure, msg = check_junk_data(data)
            if is_pure:
                total_score += 15
                score_details.append({"item": "验证数据纯净性与严格过滤", "score": 15, "max_score": 15, "passed": True, "reason": msg})
            else:
                score_details.append({"item": "验证数据纯净性与严格过滤", "score": 0, "max_score": 15, "passed": False, "reason": msg})
                
        except json.JSONDecodeError:
            score_details.append({"item": "验证 JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 解析失败"})
            score_details.append({"item": "提取目标 1", "score": 0, "max_score": 15, "passed": False, "reason": "无法解析JSON"})
            score_details.append({"item": "提取目标 2", "score": 0, "max_score": 15, "passed": False, "reason": "无法解析JSON"})
            score_details.append({"item": "提取目标 3", "score": 0, "max_score": 15, "passed": False, "reason": "无法解析JSON"})
            score_details.append({"item": "验证数据纯净性", "score": 0, "max_score": 15, "passed": False, "reason": "无法解析JSON"})
    else:
        score_details.append({"item": "验证 JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": "依赖文件不存在"})
        score_details.append({"item": "提取目标 1", "score": 0, "max_score": 15, "passed": False, "reason": "依赖文件不存在"})
        score_details.append({"item": "提取目标 2", "score": 0, "max_score": 15, "passed": False, "reason": "依赖文件不存在"})
        score_details.append({"item": "提取目标 3", "score": 0, "max_score": 15, "passed": False, "reason": "依赖文件不存在"})
        score_details.append({"item": "验证数据纯净性", "score": 0, "max_score": 15, "passed": False, "reason": "依赖文件不存在"})

    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
