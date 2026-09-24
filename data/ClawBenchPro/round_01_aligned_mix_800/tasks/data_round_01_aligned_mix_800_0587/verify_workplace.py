import os
import sys
import json
import httpx
from openai import OpenAI

# 配置环境
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
    report_path = os.path.join(workspace, "reports/final_summary.json")
    score_details = []
    total_score = 0

    # 1. 检查文件是否存在与基础格式 (10分)
    if os.path.exists(report_path):
        score_details.append({"item": "检查 final_summary.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已生成"})
        total_score += 10
    else:
        score_details.append({"item": "检查 final_summary.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件未找到"})
        # 如果文件不存在，后续无法进行，直接写入结果
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return

    # 加载 JSON 内容
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score_details.append({"item": "JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        return

    # 2. 验证幽灵工人 (Ghost Workers) 识别 (25分)
    # 根据 env_builder，ID-9999 (Ghost_1) 和 ID-8888 (Ghost_2) 是幽灵
    # 但实际 real_data 里只有 ID-9999 产生了记录
    ghost_workers = data.get("ghost_workers", [])
    # 转换为字符串列表以防万一
    ghost_str = [str(g).upper() for g in ghost_workers]
    if "ID-9999" in ghost_str or "GHOST_1" in ghost_str:
        score_details.append({"item": "识别幽灵工人 (Ghost Workers)", "score": 25, "max_score": 25, "passed": True, "reason": "成功识别出未在名单中的 ID-9999"})
        total_score += 25
    else:
        score_details.append({"item": "识别幽灵工人 (Ghost Workers)", "score": 0, "max_score": 25, "passed": False, "reason": f"未能准确识别幽灵工人，得到: {ghost_workers}"})

    # 3. 验证数据过滤逻辑 - 排除 FAKE_SITE_LOG (25分)
    # FAKE_SITE_LOG 包含 999 hours/pillars，如果总数包含这个值说明过滤失败
    # 合法总工时计算：
    # Mateo (ID-1000): 8 + 2 = 10
    # Santiago (ID-1001): 12
    # Luis (ID-1002): 10
    # Carlos (ID-1003): 4
    # Juan (ID-1004): 6
    # 合法总计: 10 + 12 + 10 + 4 + 6 = 42
    # 损耗总计: (2+1) + 1 + 0 + 3 + 0 = 7
    
    # 检查汇总逻辑是否被 FAKE 数据污染
    total_hours = data.get("total_hours", 0)
    total_pillars = data.get("total_pillars", 0)
    
    if total_hours > 500 or total_pillars > 500:
        score_details.append({"item": "噪音数据过滤 (FAKE_LOG)", "score": 0, "max_score": 25, "passed": False, "reason": "结果包含 999 等异常值，说明未能排除 FAKE 日志"})
    elif total_hours == 42 and total_pillars == 7:
        score_details.append({"item": "噪音数据过滤与精准计算", "score": 25, "max_score": 25, "passed": True, "reason": "成功过滤噪音并得出正确数值 (H:42, P:7)"})
        total_score += 25
    elif 30 < total_hours < 50:
         score_details.append({"item": "数据计算 (模糊匹配)", "score": 15, "max_score": 25, "passed": True, "reason": "数值接近正确值，但存在微小偏差"})
         total_score += 15
    else:
        score_details.append({"item": "数据计算", "score": 0, "max_score": 25, "passed": False, "reason": f"计算数值错误: H={total_hours}, P={total_pillars}"})

    # 4. 验证多语言处理与汇总结构 (20分)
    # 检查是否包含按工人汇总的明细
    worker_stats = data.get("worker_details", {})
    if len(worker_stats) >= 5:
        score_details.append({"item": "多语言日志解析与工人汇总", "score": 20, "max_score": 20, "passed": True, "reason": "成功解析多语言格式并按个人汇总"})
        total_score += 20
    else:
        score_details.append({"item": "多语言日志解析与工人汇总", "score": 0, "max_score": 20, "passed": False, "reason": "解析出的工人明细数量不足"})

    # 5. LLM 验证审计结论的严谨性 (10分)
    summary_text = str(data)
    is_professional = llm_judge_content(
        "Check if this audit report clearly lists names, UID, total hours, and mentions the presence of ghost workers. The report should look like a formal construction audit summary.",
        summary_text
    )
    if is_professional:
        score_details.append({"item": "审计报告专业性 (LLM)", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定报告结论详尽专业"})
        total_score += 10
    else:
        score_details.append({"item": "审计报告专业性 (LLM)", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定报告内容过于简略或缺失关键要素"})

    # 输出结果
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)

if __name__ == "__main__":
    verify()
