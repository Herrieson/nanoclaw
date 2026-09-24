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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    audit_dir = os.path.join(workspace, "audit_results")
    
    details = []
    total_score = 0
    
    # 1. 结构验证：检查目录是否存在 (10分)
    dir_exists = os.path.isdir(audit_dir)
    if dir_exists:
        details.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 audit_results 存在"})
        total_score += 10
    else:
        details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 audit_results 目录"})
        
    # 2. 结构验证：检查结果文件是否存在并提取内容 (10分)
    report_content = ""
    file_exists = False
    if dir_exists:
        for root, dirs, files in os.walk(audit_dir):
            for file in files:
                file_exists = True
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        report_content += f.read() + "\n"
                except Exception as e:
                    print(f"Error reading {file}: {e}")

    if file_exists and report_content.strip():
        details.append({"item": "检查报告文件是否生成并可读", "score": 10, "max_score": 10, "passed": True, "reason": "已生成至少一个结果文件且内容非空"})
        total_score += 10
    else:
        details.append({"item": "检查报告文件是否生成并可读", "score": 0, "max_score": 10, "passed": False, "reason": "目录为空或无法读取报告文件内容"})

    if not file_exists or not report_content.strip():
        report_content = "EMPTY_OR_UNREADABLE_REPORT"

    # 3. 语义与数据混合验证：利用大模型验证非法闯入者名单是否被清晰指出 (20分)
    prompt_intruders = "Analyze the following report. Does it explicitly list BOTH 'Dave Smith' and 'Unknown Person' as intruders, non-members, or uninvited guests? Answer ONLY 'YES' or 'NO'."
    if file_exists and llm_judge_content(prompt_intruders, report_content):
        details.append({"item": "检查报告是否正确识别非官方成员(Intruders)", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定正确找出了 Dave Smith 和 Unknown Person"})
        total_score += 20
    else:
        details.append({"item": "检查报告是否正确识别非官方成员(Intruders)", "score": 0, "max_score": 20, "passed": False, "reason": "未正确列出所有的非法人员，或者格式有误"})

    # 4. 语义与数据混合验证：利用大模型验证收入总额的严格计算 (20分)
    # 计算逻辑: 5*12.50 + 2*8.00 + 3*25.00 - 5.00(refund) = 148.50
    prompt_revenue = "Analyze the following report. Does it explicitly calculate and state that the final total revenue (or sales tally) is exactly $148.50 (or 148.50)? It must explicitly contain this exact calculated number. Answer ONLY 'YES' or 'NO'."
    if file_exists and llm_judge_content(prompt_revenue, report_content):
        details.append({"item": "检查销售总额计算是否正确且包含退款抵扣", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定销售总额精准为 148.50"})
        total_score += 20
    else:
        details.append({"item": "检查销售总额计算是否正确且包含退款抵扣", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定未找到正确金额 148.50（未扣除退款或计算错误）"})

    # 5. 语义与数据混合验证：利用大模型验证志愿服务时间统计及脏数据过滤 (20分)
    # Ethan: 4+3=7, Chloe: 3.5(过滤Invalid_Data), Marcus: 5, Sarah: 4
    prompt_hours = "Analyze the report. Does it explicitly list the aggregated volunteer hours for the official members accurately as follows: Ethan Miller (7 or 7.0), Chloe Chen (3.5), Marcus Thorne (5 or 5.0), and Sarah Jenkins (4 or 4.0)? All four must be exactly correct. Answer ONLY 'YES' or 'NO'."
    if file_exists and llm_judge_content(prompt_hours, report_content):
        details.append({"item": "检查官方成员时长统计与脏数据处理", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定工时统计完全正确（含对脏数据的正确抛弃）"})
        total_score += 20
    else:
        details.append({"item": "检查官方成员时长统计与脏数据处理", "score": 0, "max_score": 20, "passed": False, "reason": "时长统计错误（可能受Invalid_Data影响或未合并重复项）"})

    # 6. 非结构化语义验证：报告语气规范程度评估 (20分)
    prompt_tone = "Analyze the report. Is the overall tone highly professional, meticulously organized, respectful, and perfectly suitable to be presented to a high school faculty advisor? Answer ONLY 'YES' or 'NO'."
    if file_exists and llm_judge_content(prompt_tone, report_content):
        details.append({"item": "利用大模型检查报告专业性与格式基调", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定报告基调正式专业，符合向导师汇报的Persona"})
        total_score += 20
    else:
        details.append({"item": "利用大模型检查报告专业性与格式基调", "score": 0, "max_score": 20, "passed": False, "reason": "报告基调不够专业或结构过于杂乱"})

    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
