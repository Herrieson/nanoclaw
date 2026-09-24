import os
import sys
import json
import httpx
from openai import OpenAI

# 环境变量配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """用于非结构化语义验证的统一接口"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        res = response.choices[0].message.content.strip().lower()
        return "yes" in res
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports/summary.json")
    
    score = 0
    details = []

    # 1. 检查结果文件是否存在 (10分)
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "文件检查", "score": 10, "max_score": 10, "passed": True, "reason": "reports/summary.json 已生成"})
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 2. 验证计算逻辑：有效小时数 (40分)
            # 计算逻辑推导：
            # Alice (Active) + Under 5: 4.5 + 2.0 = 6.5
            # Charlie (Active) + Under 5: 2.5
            # Eve (Active) + Under 5: 3.0 (null忽略)
            # Diana (Expired): 0
            # Total = 6.5 + 2.5 + 3.0 = 12.0
            total_hours = data.get("total_valid_hours", 0)
            if abs(float(total_hours) - 12.0) < 0.01:
                score += 40
                details.append({"item": "计算验证: Under 5 总有效时长", "score": 40, "max_score": 40, "passed": True, "reason": f"数值 {total_hours} 正确"})
            else:
                details.append({"item": "计算验证: Under 5 总有效时长", "score": 0, "max_score": 40, "passed": False, "reason": f"数值应为 12.0，实为 {total_hours}"})

            # 3. 验证未授权名单识别 (30分)
            # 逻辑：不在 PDF 中 (Frank, Grace, Henry) 或 在 PDF 但 Expired (Diana)
            expected_unauthorized = ["Frank Castle", "Grace Lee", "Henry Todd", "Diana Prince"]
            actual_unauthorized = data.get("unauthorized_people", [])
            # 转换为集合进行不计顺序的比较
            missing = set(expected_unauthorized) - set(actual_unauthorized)
            if not missing and len(actual_unauthorized) >= 4:
                score += 30
                details.append({"item": "名单验证: 未授权人员识别", "score": 30, "max_score": 30, "passed": True, "reason": "成功识别所有未授权或过期的志愿者"})
            else:
                details.append({"item": "名单验证: 未授权人员识别", "score": 0, "max_score": 30, "passed": False, "reason": f"缺失或识别错误，缺少: {missing}"})

            # 4. 冗余字段检测 (LLM/结构化) (20分)
            # 检查是否有捏造的虚假字段或对非 Under 5 人员的错误统计
            prompt = "The report should focus on volunteers' validity and total hours for 'Under 5' children. Does this JSON contain any hallucinated names not in the log or incorrect statuses for Diana Prince?"
            if llm_judge_content(prompt, json.dumps(data)):
                score += 20
                details.append({"item": "数据合规性: 无幻觉/逻辑一致性", "score": 20, "max_score": 20, "passed": True, "reason": "报告内容符合原始数据约束，无幻觉"})
            else:
                details.append({"item": "数据合规性: 无幻觉/逻辑一致性", "score": 0, "max_score": 20, "passed": False, "reason": "报告中存在幻觉或对 Diana 的状态判定错误"})

        except Exception as e:
            details.append({"item": "格式解析", "score": 0, "max_score": 90, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
    else:
        details.append({"item": "文件检查", "score": 0, "max_score": 100, "passed": False, "reason": "reports/summary.json 不存在"})

    # 输出评分结果
    output = {"total_score": score, "details": details}
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
