import os
import sys
import json
import httpx
from openai import OpenAI

# 强制读取环境变量配置 API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型语义检测接口，统一输出 yes/no 判定"""
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

def find_numeric_value(data, target_value):
    """深度递归搜索，在未知的合法 JSON 结构中寻找确切的数值（解决格式变化，拒绝粗暴的纯文本正则表达式）"""
    if isinstance(data, dict):
        for v in data.values():
            if find_numeric_value(v, target_value): 
                return True
    elif isinstance(data, list):
        for item in data:
            if find_numeric_value(item, target_value): 
                return True
    elif isinstance(data, (int, float)):
        return data == target_value
    elif isinstance(data, str):
        try:
            return float(data) == float(target_value)
        except:
            return False
    return False

def check_workers_in_json(data):
    """深度递归搜索 JSON 中是否包含完整的劳工名单，防止幻觉造假数据"""
    workers = {"pedro", "miguel", "javier", "hector"}
    found = set()
    
    def extract_strs(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(k, str):
                    for w in workers:
                        if w in k.lower(): found.add(w)
                extract_strs(v)
        elif isinstance(obj, list):
            for i in obj:
                extract_strs(i)
        elif isinstance(obj, str):
            for w in workers:
                if w in obj.lower(): found.add(w)
                
    extract_strs(data)
    return len(found) == 4

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    target_file = os.path.join(workspace, "final_accounting", "payroll_summary.json")
    
    # Check 1: 结果目录与文件是否存在 (10分)
    if os.path.exists(target_file):
        score_details.append({"item": "检查交付报告目录与文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 payroll_summary.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查交付报告目录与文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 final_accounting/payroll_summary.json 文件"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # Check 2: 验证文件是否为合法的 JSON 格式 (15分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            file_content = f.read()
        data = json.loads(file_content)
        score_details.append({"item": "检查文件内容是否为合法的 JSON 结构", "score": 15, "max_score": 15, "passed": True, "reason": "JSON 格式解析成功"})
        total_score += 15
    except Exception as e:
        score_details.append({"item": "检查文件内容是否为合法的 JSON 结构", "score": 0, "max_score": 15, "passed": False, "reason": f"解析 JSON 失败: {e}"})
        data = None

    # Code Checks: 确定性探针校验
    if data is not None:
        # Check 3: 水泥重量的确定性提取校验 (1200 + 850 + 150 = 2200) (35分)
        if find_numeric_value(data, 2200):
            score_details.append({"item": "代码深度校验：正确汇总水泥总重量(2200 lbs)", "score": 35, "max_score": 35, "passed": True, "reason": "成功在 JSON 结构中准确匹配到目标计算结果 2200"})
            total_score += 35
        else:
            score_details.append({"item": "代码深度校验：正确汇总水泥总重量(2200 lbs)", "score": 0, "max_score": 35, "passed": False, "reason": "未找到正确的重量数值，日志解析错误或遗漏"})

        # Check 4: 劳工名单数据的确定性校验 (20分)
        if check_workers_in_json(data):
            score_details.append({"item": "代码深度校验：结构化解析中的员工名覆盖率", "score": 20, "max_score": 20, "passed": True, "reason": "完整囊括了 Pedro, Miguel, Javier, Hector 四位员工数据"})
            total_score += 20
        else:
            score_details.append({"item": "代码深度校验：结构化解析中的员工名覆盖率", "score": 0, "max_score": 20, "passed": False, "reason": "员工缺失或幻觉产生，未正确映射基础数据源"})
    else:
        score_details.append({"item": "代码深度校验：正确汇总水泥总重量", "score": 0, "max_score": 35, "passed": False, "reason": "非 JSON 格式致结构失效"})
        score_details.append({"item": "代码深度校验：结构化解析中的员工名覆盖率", "score": 0, "max_score": 20, "passed": False, "reason": "非 JSON 格式致结构失效"})

    # Check 5: LLM 检测薪资计算的合规逻辑下限 (20分)
    # 不强制校验具体金额，而是核实其是否严格执行了底薪至少 $25 以及工时相乘的数学规律。
    prompt = (
        "Does the JSON report contain payroll calculations that correctly enforce the rule: "
        "NO worker gets paid an effective rate of less than $25 per hour? "
        "For example, Pedro (40.5 hours) original rate was 15, but his effective wage total MUST be at least 1012.5 (40.5*25). "
        "Miguel (38 hours) original rate was 28, so his wage MUST be at least 1064 (38*28). "
        "Answer YES if the calculations or specific rates in the JSON successfully applied this $25 minimum threshold for all underpaid workers, otherwise NO."
    )
    passed_llm = llm_judge_content(prompt, file_content)
    if passed_llm:
        score_details.append({"item": "大模型语义校验：确保 $25 最低合规薪资底线的执行", "score": 20, "max_score": 20, "passed": True, "reason": "大模型确认计算逻辑已拉平所有低薪工人工资"})
        total_score += 20
    else:
        score_details.append({"item": "大模型语义校验：确保 $25 最低合规薪资底线的执行", "score": 0, "max_score": 20, "passed": False, "reason": "报告中遗漏了薪水对比逻辑，工人遭到克扣"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
