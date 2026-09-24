import os
import sys
import json
import httpx
import warnings
from openai import OpenAI

warnings.filterwarnings("ignore")

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
    """大模型进行非结构化长文本或语义容错判断"""
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

def extract_all_keys(obj):
    """递归提取 JSON 中的全部键，用于检测冗余捏造"""
    keys = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.append(str(k))
            keys.extend(extract_all_keys(v))
    elif isinstance(obj, list):
        for item in obj:
            keys.extend(extract_all_keys(item))
    return keys

def extract_all_values(obj):
    """递归提取 JSON 中所有基础类型的值，用于核心数值精准校验"""
    values = []
    if isinstance(obj, dict):
        for v in obj.values():
            values.extend(extract_all_values(v))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(extract_all_values(item))
    elif isinstance(obj, (str, int, float, bool)):
        values.append(str(obj).strip())
    return values

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "analysis", "culprit.json")
    
    score_details = []
    total_score = 0
    
    if not os.path.exists(report_path):
        score_details.append({
            "item": "检查结果文件及其格式", "score": 0, "max_score": 15, "passed": False,
            "reason": "目标文件 analysis/culprit.json 不存在"
        })
        score_details.extend([
            {"item": "检查是否捏造多余字段", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失，无法验证"},
            {"item": "检查是否掉入干扰陷阱", "score": 0, "max_score": 25, "passed": False, "reason": "文件缺失，无法验证"},
            {"item": "精准提取 - 源文件路径", "score": 0, "max_score": 15, "passed": False, "reason": "文件缺失，无法验证"},
            {"item": "精准提取 - 函数符号名", "score": 0, "max_score": 15, "passed": False, "reason": "文件缺失，无法验证"},
            {"item": "利用大模型检查去优化原因", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失，无法验证"}
        ])
    else:
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            score_details.append({
                "item": "检查结果文件及其格式", "score": 15, "max_score": 15, "passed": True,
                "reason": "文件存在且为完全合法的 JSON 格式"
            })
            total_score += 15
            
            all_keys = extract_all_keys(data)
            all_values = extract_all_values(data)
            all_values_lower = [str(v).lower() for v in all_values]
            
            # 1. 防止幻觉/作弊：检查结构体过度冗余
            if len(all_keys) <= 6:
                score_details.append({"item": "检查是否捏造多余字段", "score": 10, "max_score": 10, "passed": True, "reason": f"字段数量 ({len(all_keys)}) 合理，无明显捏造幻觉"})
                total_score += 10
            else:
                score_details.append({"item": "检查是否捏造多余字段", "score": 0, "max_score": 10, "passed": False, "reason": f"字段数量 ({len(all_keys)}) 异常过多，涉嫌严重捏造或输出废话噪音"})
                
            # 2. 诱饵排查：决不能包含 8888 以及附属特征
            decoy_keywords = ["lodash", "map_fast", "wrong map", "8888"]
            hit_decoy = any(any(dec in v for dec in decoy_keywords) for v in all_values_lower)
            if hit_decoy:
                score_details.append({"item": "检查是否掉入干扰陷阱", "score": 0, "max_score": 25, "passed": False, "reason": "JSON 中包含大量诱饵 script_id 8888 相关的虚假信息，Agent 试图全局统计并被诱导"})
            else:
                score_details.append({"item": "检查是否掉入干扰陷阱", "score": 25, "max_score": 25, "passed": True, "reason": "验证未被最大数量的诱饵错误干扰，方向正确"})
                total_score += 25
                
            # 3. 原生代码强制精准验证结构化信息 - Path
            expected_path = "/app/src/core/hot_path_router.js"
            if any(v == expected_path for v in all_values):
                score_details.append({"item": "精准提取 - 源文件路径", "score": 15, "max_score": 15, "passed": True, "reason": "文件路径在底层树被精准独立提取"})
                total_score += 15
            else:
                score_details.append({"item": "精准提取 - 源文件路径", "score": 0, "max_score": 15, "passed": False, "reason": f"未能找到原封不动的路径：{expected_path}"})
                
            # 4. 原生代码强制精准验证结构化信息 - Function
            expected_func = "processRequestFastPath"
            if any(v == expected_func for v in all_values):
                score_details.append({"item": "精准提取 - 函数符号名", "score": 15, "max_score": 15, "passed": True, "reason": "函数符号名在底层树被精准独立提取"})
                total_score += 15
            else:
                score_details.append({"item": "精准提取 - 函数符号名", "score": 0, "max_score": 15, "passed": False, "reason": f"未能找到原封不动的函数名：{expected_func}"})
                
            # 5. LLM 判断复杂自然语言特征 - Reason (可能组装为了短句)
            llm_prompt = "Examine the following JSON content. Does it clearly indicate that the final bailout reason is exactly 'type feedback insufficient' (ignoring casing)? Note: Do NOT accept 'wrong map'."
            file_content_str = json.dumps(data, indent=2)
            if llm_judge_content(llm_prompt, file_content_str):
                score_details.append({"item": "利用大模型检查去优化原因", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定去优化原因提取语义符合要求"})
                total_score += 20
            else:
                score_details.append({"item": "利用大模型检查去优化原因", "score": 0, "max_score": 20, "passed": False, "reason": "未通过大模型校验，缺乏关键原因 'type feedback insufficient'"})
                
        except json.JSONDecodeError:
            score_details.append({"item": "检查结果文件及其格式", "score": 0, "max_score": 15, "passed": False, "reason": "文件内容不符合 JSON 规范导致解析崩溃"})
            score_details.extend([
                {"item": "检查是否捏造多余字段", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 解析失败，无法验证"},
                {"item": "检查是否掉入干扰陷阱", "score": 0, "max_score": 25, "passed": False, "reason": "JSON 解析失败，无法验证"},
                {"item": "精准提取 - 源文件路径", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 解析失败，无法验证"},
                {"item": "精准提取 - 函数符号名", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 解析失败，无法验证"},
                {"item": "利用大模型检查去优化原因", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 解析失败，无法验证"}
            ])
            
    # 写入最终判决文件
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
