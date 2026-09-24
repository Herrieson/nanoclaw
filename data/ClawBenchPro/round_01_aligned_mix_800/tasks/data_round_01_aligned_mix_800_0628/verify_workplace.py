import os
import sys
import json
import csv
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
    report_dir = os.path.join(workspace, "inventory_reports")
    
    score_details = []
    total_score = 0
    
    # 1. 目录存在性 (10分)
    dir_exists = os.path.isdir(report_dir)
    if dir_exists:
        score_details.append({"item": "检查目标目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "inventory_reports 目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "inventory_reports 目录缺失"})
        
    # 2. 报告文件存在性 (10分)
    report_files = []
    if dir_exists:
        report_files = [f for f in os.listdir(report_dir) if os.path.isfile(os.path.join(report_dir, f))]
        
    if report_files:
        score_details.append({"item": "检查报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": f"找到文件: {report_files[0]}"})
        total_score += 10
    else:
        score_details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未在目录中找到任何报告文件"})
        
    # 如果没有文件，直接返回
    if not report_files:
        _write_results(total_score, score_details, workspace)
        return

    report_path = os.path.join(report_dir, report_files[0])
    with open(report_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read().strip()
        
    # 尝试结构化解析 (JSON / CSV)
    is_structured = False
    parsed_dict = {}
    
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            parsed_dict = {k.lower(): str(v) for k, v in data.items()}
            is_structured = True
    except:
        pass
        
    if not is_structured and "," in content and "\n" in content:
        try:
            reader = csv.reader(content.split("\n"))
            for row in reader:
                if len(row) >= 2:
                    parsed_dict[row[0].lower().strip()] = row[1].strip()
            if parsed_dict:
                is_structured = True
        except:
            pass

    # 3. 验证 Shea Butter 数量 = 650 (25分)
    passed_shea = False
    if is_structured:
        passed_shea = any("shea butter" in k and "650" in v for k, v in parsed_dict.items())
    else:
        passed_shea = llm_judge_content("Does the file state that the total combined weight of 'Shea Butter' is exactly 650? Answer YES if true, NO if false or missing.", content)
        
    if passed_shea:
        score_details.append({"item": "验证 Shea Butter 汇总计算准确性", "score": 25, "max_score": 25, "passed": True, "reason": "准确计算出 Shea Butter 的总重为 650"})
        total_score += 25
    else:
        score_details.append({"item": "验证 Shea Butter 汇总计算准确性", "score": 0, "max_score": 25, "passed": False, "reason": "未能准确输出 Shea Butter 的重量为 650（可能未合并多批次）"})

    # 4. 验证 Lavender Oil 数量 = 50 (20分)
    passed_lavender = False
    if is_structured:
        passed_lavender = any("lavender" in k and "50" in v and "10" not in v for k, v in parsed_dict.items())
    else:
        passed_lavender = llm_judge_content("Does the file state that the total weight of 'Lavender Oil' is exactly 50? (It must NOT be 60 or 10). Answer YES only if it clearly states 50.", content)
        
    if passed_lavender:
        score_details.append({"item": "验证 Lavender Oil 汇总及过滤逻辑", "score": 20, "max_score": 20, "passed": True, "reason": "准确排除 Pending 批次，计算得 50"})
        total_score += 20
    else:
        score_details.append({"item": "验证 Lavender Oil 汇总及过滤逻辑", "score": 0, "max_score": 20, "passed": False, "reason": "未能输出 Lavender Oil 为 50（可能错误包含了 Pending 批次）"})

    # 5. 验证 Rose Water 数量 = 30 (20分)
    passed_rose = False
    if is_structured:
        passed_rose = any("rose water" in k and "30" in v for k, v in parsed_dict.items())
    else:
        passed_rose = llm_judge_content("Does the file state that the total weight of 'Rose Water' is exactly 30? Answer YES if true.", content)
        
    if passed_rose:
        score_details.append({"item": "验证非标准日志文件的提取", "score": 20, "max_score": 20, "passed": True, "reason": "成功从 TXT 日志中解析并保留了 Rose Water"})
        total_score += 20
    else:
        score_details.append({"item": "验证非标准日志文件的提取", "score": 0, "max_score": 20, "passed": False, "reason": "未能正确从 batch_B.txt 中提取到 Rose Water 的数据"})

    # 6. 验证是否包含错误数据 (15分)
    has_invalid = False
    if is_structured:
        invalid_keys = ['lye', 'coconut', 'dye', 'napkin', 'guest']
        has_invalid = any(any(inv in k for inv in invalid_keys) for k in parsed_dict.keys())
    else:
        has_invalid = llm_judge_content("Does the file include ANY weights, counts, or references to 'Lye', 'Coconut Oil', 'Artificial Dye', or 'napkins/guests'? Answer YES if ANY of these are mentioned in the totals/report, NO if they are completely excluded.", content)
        
    if not has_invalid:
        score_details.append({"item": "剔除污染数据与干扰项", "score": 15, "max_score": 15, "passed": True, "reason": "报告纯净，完美剔除了 Rejected/Pending 数据和派对名单干扰"})
        total_score += 15
    else:
        score_details.append({"item": "剔除污染数据与干扰项", "score": 0, "max_score": 15, "passed": False, "reason": "报告中混入了被拒绝、待定状态的原料，或包含了无关的客单/纸巾数据"})

    _write_results(total_score, score_details, workspace)

def _write_results(total_score, score_details, workspace):
    result = {
        "total_score": total_score,
        "details": score_details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Workplace validation completed. Score: {total_score}/100")

if __name__ == "__main__":
    verify()
