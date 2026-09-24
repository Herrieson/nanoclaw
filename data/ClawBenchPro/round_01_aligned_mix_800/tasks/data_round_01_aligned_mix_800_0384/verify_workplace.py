import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

# 关闭 SSL 验证，初始化客户端
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

def verify_workplace(workspace):
    score_details = []
    total_score = 0
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    # 1. 检查交付物目录与文件 (10分)
    report_file_path = None
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        files = [f for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]
        if files:
            # 找到任意一个生成的文件作为报告
            report_file_path = os.path.join(deliverables_dir, files[0])
            score_details.append({
                "item": "检查结果目录与报告文件是否存在",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": f"成功找到报告文件: {files[0]}"
            })
            total_score += 10
        else:
            score_details.append({
                "item": "检查结果目录与报告文件是否存在",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "deliverables 目录存在但无文件"
            })
    else:
        score_details.append({
            "item": "检查结果目录与报告文件是否存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "deliverables 目录不存在"
        })

    # 如果没有报告，直接返回失败
    if not report_file_path:
        for item in ["关键结果：正确计算核准志愿者总工时", "关键结果：精准识别被拒志愿者", "语义提取：汇总紧急物资需求"]:
            score_details.append({
                "item": item,
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": "报告文件缺失，无法进行验证"
            })
        
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 读取报告内容
    try:
        with open(report_file_path, "r", encoding="utf-8") as f:
            report_content = f.read()
    except Exception as e:
        report_content = ""

    # 2. 关键结果：正确计算核准志愿者总工时 (30分)
    # 正确逻辑：Sarah(4.5+1.5) + Ellen(3) + Miles(8) = 17.0 小时 (John 2.5 和 T-800 12.0 被拒绝)
    prompt_hours = "Does the text explicitly state that the total valid hours for APPROVED volunteers is exactly 17 or 17.0? Answer YES only if 17 (or 17.0) is clearly identified as the final sum of hours for approved/cleared volunteers."
    if llm_judge_content(prompt_hours, report_content):
        score_details.append({"item": "关键结果：正确计算核准志愿者总工时", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定正确计算出了17小时的核准工时"})
        total_score += 30
    else:
        score_details.append({"item": "关键结果：正确计算核准志愿者总工时", "score": 0, "max_score": 30, "passed": False, "reason": "未找到正确的核准工时(17.0)或存在幻觉捏造"})

    # 3. 关键结果：精准识别被拒志愿者 (30分)
    # 正确逻辑：John Smith 和 T-800
    prompt_denied = "Does the text explicitly identify BOTH 'John Smith' and 'T-800' as the unapproved, denied, or failed volunteers? Answer YES only if both names are clearly flagged as failing the background check."
    if llm_judge_content(prompt_denied, report_content):
        score_details.append({"item": "关键结果：精准识别被拒志愿者", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定准确识别出了John Smith与T-800作为违规人员"})
        total_score += 30
    else:
        score_details.append({"item": "关键结果：精准识别被拒志愿者", "score": 0, "max_score": 30, "passed": False, "reason": "未正确列出被拒绝的违规人员，漏报或出现幻觉"})

    # 4. 语义提取：汇总紧急物资需求 (30分)
    # 正确逻辑：Baby formula and diapers, Pediatric asthma inhaler assistance, Bus passes
    prompt_needs = "Does the text explicitly extract and list the following urgent community needs: 1) Baby formula/diapers, 2) Pediatric asthma inhaler, and 3) Bus passes? Answer YES only if all three urgent items are mentioned and correctly flagged as urgent."
    if llm_judge_content(prompt_needs, report_content):
        score_details.append({"item": "语义提取：汇总紧急物资需求", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定成功提取了对婴儿/儿童及急需家庭的紧急物资列表"})
        total_score += 30
    else:
        score_details.append({"item": "语义提取：汇总紧急物资需求", "score": 0, "max_score": 30, "passed": False, "reason": "遗漏了紧急物资或混入了非紧急（如冬衣、罐头）物资"})

    # 写入最终得分
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace_dir)
