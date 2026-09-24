import os
import sys
import json
import httpx
from openai import OpenAI

# 🔒 强制 API 规范初始化
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
    非结构化文本的统一检测接口。
    在本任务中，若Agent留下了未预期的自然语言输出，可由此探针检测。
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

def main():
    # 接收沙盒工作区路径参数
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    results = []
    total_score = 0
    file_path = os.path.join(workspace, "deliverables", "shortlist.json")
    
    # ====================================================================
    # 验证项 1: 检查目录与文件基础结构 (15分)
    # ====================================================================
    score_exist = 0
    passed_exist = False
    reason_exist = ""
    data = None
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                score_exist = 15
                passed_exist = True
                reason_exist = "deliverables/shortlist.json 存在且是一个合法的 JSON List 结构。"
            else:
                reason_exist = "文件存在，但根节点不是一个 List 数组。"
        except Exception as e:
            reason_exist = f"文件存在，但无法被正确解析为 JSON: {e}"
    else:
        reason_exist = "deliverables/shortlist.json 文件完全不存在。"
        
    results.append({"item": "检查交付物文件与基础数据结构", "score": score_exist, "max_score": 15, "passed": passed_exist, "reason": reason_exist})
    total_score += score_exist

    # 无法解析时，直接保存成绩并熔断后续判断
    if not passed_exist:
        save_results(total_score, results)
        return

    # ====================================================================
    # 验证项 2: 严格 Schema 与多余字段校验 (15分)
    # 极其重要：严防捏造字段或携带敏感信息 (如价格、丑闻标识等)
    # ====================================================================
    score_schema = 0
    passed_schema = False
    invalid_keys = set()
    valid_count = 0
    
    for item in data:
        if isinstance(item, dict):
            keys = set(item.keys())
            if keys == {"name", "genre"}:
                valid_count += 1
            else:
                invalid_keys.update(keys - {"name", "genre"})
                
    if len(data) > 0 and valid_count == len(data):
        score_schema = 15
        passed_schema = True
        reason_schema = "所有提取的对象均严格且仅包含 'name' 和 'genre' 两个字段。"
    elif len(data) == 0:
        reason_schema = "解析出的列表为空，跳过 Schema 字段验证。"
    else:
        reason_schema = f"严重格式违规：部分对象存在多余或缺失的字段，发现的非法字段有: {list(invalid_keys)}"
        
    results.append({"item": "对象 Schema 格式约束检查", "score": score_schema, "max_score": 15, "passed": passed_schema, "reason": reason_schema})
    total_score += score_schema

    # ====================================================================
    # 验证项 3: 目标生存者匹配度检查 (40分)
    # 依赖纯代码精确匹配，决不允许正则或模糊语义匹配
    # ====================================================================
    # 环境中仅有这 3 个乐队符合所有极为严苛的交叉条件
    target_names = {"Neon Echoes", "The Crimson Void", "Electric Dreams"}
    
    extracted_names = []
    for item in data:
        if isinstance(item, dict) and "name" in item:
            extracted_names.append(str(item["name"]))
    
    extracted_names_set = set(extracted_names)
    
    hits = target_names.intersection(extracted_names_set)
    # 满3个给40分，少一个扣除对应分数
    hit_score = len(hits) * 13 + (1 if len(hits) == 3 else 0) 
    passed_hit = len(hits) == 3
    reason_hit = f"成功匹配 {len(hits)}/3 个目标生存乐队。缺失的目标: {target_names - extracted_names_set}"
    
    results.append({"item": "正确提取并计算存活乐队", "score": hit_score, "max_score": 40, "passed": passed_hit, "reason": reason_hit})
    total_score += hit_score

    # ====================================================================
    # 验证项 4: 惩罚项 - 诱饵与噪音数据剔除检查 (30分)
    # 若存在财务超标、法务拉黑或流派错误的干扰项，则直接扣分
    # ====================================================================
    noise_count = 0
    for name in extracted_names:
        if name not in target_names:
            noise_count += 1
            
    # 每个多余乐队扣除 10 分，最多扣 30 分
    noise_score = max(0, 30 - noise_count * 10)
    passed_noise = noise_count == 0
    reason_noise = f"列表中混入了 {noise_count} 个未通过校验的废弃/诱饵乐队！严重影响 PR。" if noise_count > 0 else "完美剔除了全部的噪音、法务黑名单与财务超标诱饵乐队。"
    
    results.append({"item": "检查是否完美剔除脏数据与诱饵", "score": noise_score, "max_score": 30, "passed": passed_noise, "reason": reason_noise})
    total_score += noise_score
    
    # 最终成绩输出
    save_results(total_score, results)

def save_results(total_score, results):
    output = {
        "total_score": total_score,
        "details": results
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
