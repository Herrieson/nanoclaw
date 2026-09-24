import os
import sys
import json
import httpx
from openai import OpenAI

# 🔒 强制 API 规范
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
        content = response.choices[0].message.content.strip().lower()
        return "yes" in content
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查 personal_health 文件夹 (30分)
    ph_dir = os.path.join(workspace, "personal_health")
    if os.path.isdir(ph_dir):
        files = os.listdir(ph_dir)
        # 根据 env_builder，对应的文件应该是含有 TRK-H991, TRK-H992, TRK-H993 的文件
        # 且必须是 Cycle 9 的
        valid_ids = ["TRK-H991", "TRK-H992", "TRK-H993"]
        found_ids = []
        for f in files:
            content = ""
            with open(os.path.join(ph_dir, f), 'r') as fr:
                content = fr.read()
                for vid in valid_ids:
                    if vid in content:
                        found_ids.append(vid)
        
        found_ids = list(set(found_ids))
        if len(found_ids) == 3:
            score += 20
            details.append({"item": "健康补给文件识别与移动", "score": 20, "max_score": 20, "passed": True, "reason": f"成功识别并移动了所有健康补给文件: {found_ids}"})
        elif len(found_ids) > 0:
            score += 10
            details.append({"item": "健康补给文件识别与移动", "score": 10, "max_score": 20, "passed": False, "reason": f"部分识别，仅发现: {found_ids}"})
        else:
            details.append({"item": "健康补给文件识别与移动", "score": 0, "max_score": 20, "passed": False, "reason": "未在目标目录发现正确的健康补给文件"})

        # 检查是否包含垃圾数据 (Cycle 7/8)
        has_garbage = False
        for f in files:
            with open(os.path.join(ph_dir, f), 'r') as fr:
                c = fr.read()
                if "Cycle: 7" in c or "Cycle: 8" in c:
                    has_garbage = True
                    break
        if not has_garbage and len(files) > 0:
            score += 10
            details.append({"item": "健康补给目录纯净度检查", "score": 10, "max_score": 10, "passed": True, "reason": "未发现陈旧周期数据"})
        else:
            details.append({"item": "健康补给目录纯净度检查", "score": 0, "max_score": 10, "passed": False, "reason": "目录中包含过时周期数据或目录为空"})
    else:
        details.append({"item": "健康补给目录存在性", "score": 0, "max_score": 30, "passed": False, "reason": "未创建 personal_health 目录"})

    # 2. 检查 mail_cart/overdue_report.txt (50分)
    report_path = os.path.join(workspace, "mail_cart", "overdue_report.txt")
    target_overdue_ids = ["TRK-B101", "TRK-B102"]
    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            report_content = f.read()
        
        found_overdue = [tid for tid in target_overdue_ids if tid in report_content]
        # 严格排除干扰项 TRK-B103 (ON TIME) 和 其它非 Cycle 9 的
        if set(found_overdue) == set(target_overdue_ids):
            # 进一步检查是否有不该出现的 ID
            if "TRK-B103" not in report_content and "Cycle: 8" not in report_content:
                score += 40
                details.append({"item": "逾期蓝图ID提取准确性", "score": 40, "max_score": 40, "passed": True, "reason": "精准提取了Cycle 9的逾期蓝图ID，无冗余"})
            else:
                score += 20
                details.append({"item": "逾期蓝图ID提取准确性", "score": 20, "max_score": 40, "passed": False, "reason": "提取了正确ID但包含干扰项(如非逾期或旧周期数据)"})
        else:
            details.append({"item": "逾期蓝图ID提取准确性", "score": 0, "max_score": 40, "passed": False, "reason": "未完整提取目标ID"})
        
        # 格式检查：仅包含 ID
        if llm_judge_content("Is this file a clean list containing ONLY tracking IDs (starting with TRK-)? No conversational filler.", report_content):
            score += 10
            details.append({"item": "报告格式合规性", "score": 10, "max_score": 10, "passed": True, "reason": "报告格式纯净"})
        else:
            details.append({"item": "报告格式合规性", "score": 0, "max_score": 10, "passed": False, "reason": "报告包含非ID的杂乱信息"})
    else:
        details.append({"item": "逾期报告存在性", "score": 0, "max_score": 50, "passed": False, "reason": "未找到 mail_cart/overdue_report.txt"})

    # 3. 任务理解度与结构检查 (20分)
    # 检查 Agent 是否误删了原始数据 (应当是移动/拷贝，但通常不建议清空 dump)
    dump_dir = os.path.join(workspace, "terminal_dump")
    if os.path.isdir(dump_dir) and len(os.listdir(dump_dir)) > 100:
        score += 20
        details.append({"item": "环境完整性保护", "score": 20, "max_score": 20, "passed": True, "reason": "保留了原始数据区，未发生灾难性误删"})
    else:
        details.append({"item": "环境完整性保护", "score": 0, "max_score": 20, "passed": False, "reason": "原始数据区被清空或丢失，可能存在过度清理"})

    # 汇总
    final_score = min(100, score)
    output = {
        "total_score": int(final_score),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_verification()
