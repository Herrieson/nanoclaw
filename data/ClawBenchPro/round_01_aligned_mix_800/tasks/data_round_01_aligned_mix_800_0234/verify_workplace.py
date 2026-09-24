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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    for_sale_dir = os.path.join(workspace, "for_sale")
    catalog_path = os.path.join(for_sale_dir, "catalog.json")
    summary_path = os.path.join(for_sale_dir, "summary.txt")

    details = []
    total_score = 0

    # 1. 检查目录与文件存在性 (10分)
    files_exist = os.path.isdir(for_sale_dir) and os.path.exists(catalog_path) and os.path.exists(summary_path)
    if files_exist:
        details.append({"item": "检查输出目录及核心文件", "score": 10, "max_score": 10, "passed": True, "reason": "for_sale 目录及 JSON/TXT 文件均存在"})
        total_score += 10
    else:
        details.append({"item": "检查输出目录及核心文件", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 for_sale 目录或其下必要文件"})
        # 如果文件都不存在，直接返回
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. 检查 catalog.json 格式合法性 (10分)
    catalog_data = None
    try:
        with open(catalog_path, "r") as f:
            catalog_data = json.load(f)
        if isinstance(catalog_data, list) and len(catalog_data) > 0:
            details.append({"item": "catalog.json 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析为非空 JSON 列表"})
            total_score += 10
        else:
            raise ValueError("不是非空列表")
    except Exception as e:
        details.append({"item": "catalog.json 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败或不是有效列表: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 提取信息进行校验
    titles = [str(item.get("Title", "")).lower() for item in catalog_data]
    
    # 3. 检查去重逻辑与高分保留 (20分)
    asm_count = sum(1 for t in titles if "spider-man" in t)
    asm_item = next((item for item in catalog_data if "spider-man" in str(item.get("Title", "")).lower()), None)
    
    if asm_count == 1 and asm_item and float(asm_item.get("Condition_Score", 0)) == 9.4 and float(asm_item.get("Market_Value", 0)) == 2800:
        details.append({"item": "去重逻辑与保留高分", "score": 20, "max_score": 20, "passed": True, "reason": "The Amazing Spider-Man #129 成功去重并保留了 9.4 高分版"})
        total_score += 20
    else:
        details.append({"item": "去重逻辑与保留高分", "score": 0, "max_score": 20, "passed": False, "reason": "Spider-Man 重复存在或保留了低分/错误分值版本"})

    # 4. 检查过滤逻辑 (15分)
    has_xmen = any("x-men" in t for t in titles)
    if not has_xmen:
        details.append({"item": "低分过滤逻辑", "score": 15, "max_score": 15, "passed": True, "reason": "成功过滤掉了分数 < 6.0 的 X-Men"})
        total_score += 15
    else:
        details.append({"item": "低分过滤逻辑", "score": 0, "max_score": 15, "passed": False, "reason": "发现了本应被过滤的低分漫画"})

    # 5. 检查外部工具查询与 PDF 数据合并 (20分)
    has_ff48 = False
    has_avengers4 = False
    for item in catalog_data:
        title_lower = str(item.get("Title", "")).lower()
        if "fantastic four" in title_lower and str(item.get("Issue", "")) == "48":
            if float(item.get("Market_Value", 0)) == 4500 and float(item.get("Condition_Score", 0)) == 9.0:
                has_ff48 = True
        if "avengers" in title_lower and str(item.get("Issue", "")) == "4":
            if float(item.get("Market_Value", 0)) == 3000 and float(item.get("Condition_Score", 0)) == 9.0:
                has_avengers4 = True

    if has_ff48 and has_avengers4:
        details.append({"item": "API查价与加密数据源整合", "score": 20, "max_score": 20, "passed": True, "reason": "成功补全 FF48 价格并解析了 PDF 中的 Avengers 4"})
        total_score += 20
    else:
        details.append({"item": "API查价与加密数据源整合", "score": 0, "max_score": 20, "passed": False, "reason": "缺少 FF48 的准确补全或未能整合 vault_index.pdf 数据"})

    # 6. 检查降序排序逻辑 (15分)
    try:
        values = [float(item.get("Market_Value", 0)) for item in catalog_data]
        if values == sorted(values, reverse=True) and len(values) >= 5:
            details.append({"item": "价值降序排序", "score": 15, "max_score": 15, "passed": True, "reason": "数据列表严格按照 Market_Value 降序排列"})
            total_score += 15
        else:
            raise ValueError("排序不符合要求")
    except Exception as e:
        details.append({"item": "价值降序排序", "score": 0, "max_score": 15, "passed": False, "reason": "未能按价值正确降序排列或数据量异常"})

    # 7. LLM 评估 Summary (10分)
    try:
        with open(summary_path, "r") as f:
            summary_content = f.read()
        
        prompt = "Check if the summary text meets ALL these conditions: 1) Mentions total items are 6. 2) Mentions total estimated value is exactly 17600. 3) The tone is heartfelt, empathetic, or encouraging towards an unemployed father."
        if llm_judge_content(prompt, summary_content):
            details.append({"item": "大模型语义检查: 总结报告", "score": 10, "max_score": 10, "passed": True, "reason": "总结文字的情感、总价和总数量均正确无误"})
            total_score += 10
        else:
            details.append({"item": "大模型语义检查: 总结报告", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定数量、金额或情感基调不符"})
    except Exception as e:
         details.append({"item": "大模型语义检查: 总结报告", "score": 0, "max_score": 10, "passed": False, "reason": "读取 summary.txt 失败"})

    # 输出结果
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
