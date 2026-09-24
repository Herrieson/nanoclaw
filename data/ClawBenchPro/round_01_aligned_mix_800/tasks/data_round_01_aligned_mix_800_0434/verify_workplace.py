import os
import sys
import json
import httpx
from openai import OpenAI

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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    
    for_sale_dir = os.path.join(workspace, "for_sale")
    catalog_path = os.path.join(for_sale_dir, "catalog.json")
    summary_path = os.path.join(for_sale_dir, "summary.txt")

    # 1. 检查目录和文件是否存在 (10分)
    passed_files = os.path.exists(catalog_path) and os.path.exists(summary_path)
    score = 10 if passed_files else 0
    total_score += score
    results.append({
        "item": "目录与输出文件存在",
        "score": score,
        "max_score": 10,
        "passed": passed_files,
        "reason": "for_sale 目录及 catalog.json, summary.txt 均存在" if passed_files else "缺失目录或必备文件"
    })

    if not passed_files:
        # 如果连文件都没有，后续验证无意义
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2)
        return

    # 尝试解析 catalog.json
    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
    except Exception as e:
        results.append({
            "item": "Catalog 格式合法性",
            "score": 0,
            "max_score": 90,
            "passed": False,
            "reason": f"解析 JSON 失败: {e}"
        })
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2)
        return

    # 2. 检查排序是否正确 (20分)
    try:
        market_values = [float(item.get("Market_Value", 0)) for item in catalog]
        is_sorted = all(market_values[i] >= market_values[i+1] for i in range(len(market_values)-1))
        score = 20 if is_sorted else 0
        total_score += score
        results.append({
            "item": "Catalog 数值降序排列",
            "score": score,
            "max_score": 20,
            "passed": is_sorted,
            "reason": "Market_Value 按降序排列" if is_sorted else "未按 Market_Value 降序排列"
        })
    except Exception as e:
        results.append({
            "item": "Catalog 数值降序排列",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"提取排序值失败，可能存在非数值类型: {e}"
        })

    # 3. 检查数据精确过滤与去重 (40分 = 4 * 10)
    has_fake = any(item.get("Title") == "Action Comics" and item.get("Issue") == "1" for item in catalog)
    has_low_score = any(float(item.get("Condition_Score", 10)) < 6.0 for item in catalog)
    has_empty_value = any(str(item.get("Market_Value", "")).strip() == "" for item in catalog)
    
    # 查找 Spider-Man #129 验证去重逻辑是否保留了最高分
    spiderman_item = next((item for item in catalog if item.get("Title") == "The Amazing Spider-Man" and item.get("Issue") == "129"), None)
    spiderman_correct = False
    if spiderman_item:
        if float(spiderman_item.get("Condition_Score", 0)) == 9.8 and float(spiderman_item.get("Market_Value", 0)) == 4500.0:
            spiderman_correct = True

    checks = [
        ("未包含伪造数据", not has_fake, "成功剔除了 shadow_copy 中的高额陷阱数据", "未甄别 STATUS: VERIFIED，包含了假数据"),
        ("剔除低评分漫画", not has_low_score, "成功过滤了 Condition_Score < 6.0 的数据", "存在 Condition_Score < 6.0 的数据"),
        ("剔除空价值漫画", not has_empty_value, "成功过滤了 Market_Value 为空的数据", "存在 Market_Value 为空的数据"),
        ("正确合并并保留最高分", spiderman_correct, "Spider-Man #129 正确保留了 9.8 评分的版本", "未能按 Title 和 Issue 合并，或未能保留最高评分记录")
    ]

    for name, passed, ok_msg, err_msg in checks:
        score = 10 if passed else 0
        total_score += score
        results.append({
            "item": name,
            "score": score,
            "max_score": 10,
            "passed": passed,
            "reason": ok_msg if passed else err_msg
        })

    # 4. LLM 验证非结构化的 summary.txt (30分)
    # 计算当前 catalog 中的总和与总数，以便提供给 LLM 比对
    actual_count = len(catalog)
    try:
        actual_total_value = sum(float(item.get("Market_Value", 0)) for item in catalog)
    except:
        actual_total_value = 0

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            summary_content = f.read()
            
        prompt = (f"Does this summary text clearly state that the total count of items is exactly {actual_count} "
                  f"AND the total market value is exactly {actual_total_value}?")
        llm_pass = llm_judge_content(prompt, summary_content)
        
        score = 30 if llm_pass else 0
        total_score += score
        results.append({
            "item": "Summary 数据语义核对",
            "score": score,
            "max_score": 30,
            "passed": llm_pass,
            "reason": f"大模型判定汇总正确，总量 {actual_count} 与总价值匹配" if llm_pass else "大模型判定内容中存在错误的值或未包含必要信息"
        })
    except Exception as e:
         results.append({
            "item": "Summary 数据语义核对",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"读取 summary.txt 异常: {e}"
        })

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2)

if __name__ == "__main__":
    main()
