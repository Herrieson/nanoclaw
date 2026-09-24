import os
import sys
import json
import math
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
    report_path = os.path.join(workspace, "audit_report", "summary.json")
    
    score_details = []
    total_score = 0
    
    # 1. 检查结果文件是否存在 (10分)
    if not os.path.exists(report_path):
        score_details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 audit_report/summary.json 不存在"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2)
        return
    else:
        score_details.append({"item": "检查报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 audit_report/summary.json 存在"})
        total_score += 10

    # 2. 读取并解析 JSON 结构 (10分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        
        required_keys = {"high_risk_families", "external_flags", "invalid_records_count", "average_risk_index"}
        if required_keys.issubset(set(report_data.keys())):
            score_details.append({"item": "检查报告 JSON 字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "所需字段完整"})
            total_score += 10
        else:
            score_details.append({"item": "检查报告 JSON 字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失字段。期望包含: {required_keys}"})
    except Exception as e:
        score_details.append({"item": "检查报告 JSON 字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 3. 验证 invalid_records_count (20分)
    invalid_count = report_data.get("invalid_records_count", 0)
    if invalid_count == 2:
        score_details.append({"item": "验证异常数据剔除能力", "score": 20, "max_score": 20, "passed": True, "reason": "准确排除了2条未来日期的数据"})
        total_score += 20
    else:
        score_details.append({"item": "验证异常数据剔除能力", "score": 0, "max_score": 20, "passed": False, "reason": f"应排除2条记录，实际提取值为: {invalid_count}"})

    # 4. 验证 high_risk_families (30分)
    # Kim, Smith, Lee 是符合高风险条件的有效家庭
    # Kim: index > 0.7; Smith: index > 0.7; Lee: score < 40 (39)
    high_risk = report_data.get("high_risk_families", [])
    if isinstance(high_risk, list):
        hr_lower = [str(x).lower().strip() for x in high_risk]
        expected_set = {"kim", "smith", "lee"}
        actual_set = set(hr_lower)
        
        if expected_set == actual_set:
            score_details.append({"item": "精准识别特级关注家庭", "score": 30, "max_score": 30, "passed": True, "reason": "精确匹配高风险家庭名单"})
            total_score += 30
        elif expected_set.issubset(actual_set) and len(actual_set) <= 4:
            score_details.append({"item": "精准识别特级关注家庭", "score": 15, "max_score": 30, "passed": False, "reason": "包含正确名单但混入了错误家庭"})
            total_score += 15
        else:
            score_details.append({"item": "精准识别特级关注家庭", "score": 0, "max_score": 30, "passed": False, "reason": f"名单不符，期望: {list(expected_set)}，实际: {list(actual_set)}"})
    else:
        score_details.append({"item": "精准识别特级关注家庭", "score": 0, "max_score": 30, "passed": False, "reason": "数据格式不合法，应为列表"})

    # 5. 验证 average_risk_index (15分)
    # 计算均值：Kim(0.845) + Garcia(0.12) + Smith(1.0) + Lee(0.61) + Muller(0.58) = 3.155 / 5 = 0.631
    avg_index = report_data.get("average_risk_index", 0)
    try:
        avg_index_float = float(avg_index)
        if math.isclose(avg_index_float, 0.631, abs_tol=0.01):
            score_details.append({"item": "验证风险指数数学计算精度", "score": 15, "max_score": 15, "passed": True, "reason": f"计算均值 {avg_index_float} 非常准确"})
            total_score += 15
        elif math.isclose(avg_index_float, 0.631, abs_tol=0.1):
            score_details.append({"item": "验证风险指数数学计算精度", "score": 5, "max_score": 15, "passed": False, "reason": f"计算均值 {avg_index_float} 偏差较大"})
            total_score += 5
        else:
            score_details.append({"item": "验证风险指数数学计算精度", "score": 0, "max_score": 15, "passed": False, "reason": f"计算错误，与期望值 0.631 相差甚远"})
    except:
        score_details.append({"item": "验证风险指数数学计算精度", "score": 0, "max_score": 15, "passed": False, "reason": "字段非数值"})

    # 6. 验证 external_flags (15分)
    # Smith 肯定为 True，其他可能因为 LLM Mock 也是 True，所以必须 >= 1 且 <= 5
    flags = report_data.get("external_flags", 0)
    try:
        flags_int = int(flags)
        if 1 <= flags_int <= 5:
            score_details.append({"item": "验证外部违规查询结果", "score": 15, "max_score": 15, "passed": True, "reason": "至少捕获到了必现的 Smith 的历史记录"})
            total_score += 15
        else:
            score_details.append({"item": "验证外部违规查询结果", "score": 0, "max_score": 15, "passed": False, "reason": f"外部历史查询结果不合理: {flags_int}"})
    except:
        score_details.append({"item": "验证外部违规查询结果", "score": 0, "max_score": 15, "passed": False, "reason": "字段非整数"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
