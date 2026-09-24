import os
import sys
import json
import re
import httpx
from openai import OpenAI

# 强制约定的 Mock 环境变量配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型辅助的非结构化语义探针"""
    if not file_content.strip():
        return False
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
    deliverable_dir = os.path.join(workspace, "garden_deliverables")
    
    score_details = []
    total_score = 0
    file_content = ""

    # 1. 检查目标目录是否存在 (10分)
    dir_exists = os.path.isdir(deliverable_dir)
    if dir_exists:
        total_score += 10
        score_details.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "garden_deliverables 目录存在"})
    else:
        score_details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "garden_deliverables 目录不存在"})

    # 2. 检查输出文件是否存在并读取内容 (10分)
    files = os.listdir(deliverable_dir) if dir_exists else []
    has_files = len(files) > 0
    if has_files:
        total_score += 10
        score_details.append({"item": "检查目录内是否生成了总结文件", "score": 10, "max_score": 10, "passed": True, "reason": "发现了输出文件"})
        # 读取所有文件内容组合
        for f in files:
            file_path = os.path.join(deliverable_dir, f)
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    file_content += file.read() + "\n"
    else:
        score_details.append({"item": "检查目录内是否生成了总结文件", "score": 0, "max_score": 10, "passed": False, "reason": "未找到任何输出文件"})

    # 3. 数据精确匹配：批准的人员名单 (25分)
    # Alice, Charlie, Eve, Grace 申请了安全的植物
    approved_names = ["alice", "charlie", "eve", "grace"]
    missing_names = [name for name in approved_names if name not in file_content.lower()]
    if has_files and not missing_names:
        total_score += 25
        score_details.append({"item": "验证全部合法志愿者是否均在报告中", "score": 25, "max_score": 25, "passed": True, "reason": "包含所有应被批准的志愿者姓名"})
    else:
        score_details.append({"item": "验证全部合法志愿者是否均在报告中", "score": 0, "max_score": 25, "passed": False, "reason": f"缺失的志愿者: {missing_names}"})

    # 4. 数据精确匹配：总时长统计验证 (25分)
    # Alice(5) + Charlie(3) + Eve(4) + Grace(2) = 14
    if has_files and re.search(r'\b14\b', file_content):
        total_score += 25
        score_details.append({"item": "计算结果提取与验证", "score": 25, "max_score": 25, "passed": True, "reason": "精准提取到合法的总志愿时长 '14'"})
    else:
        score_details.append({"item": "计算结果提取与验证", "score": 0, "max_score": 25, "passed": False, "reason": "未能在输出中提取到正确的总志愿时长数值 14"})

    # 5. LLM 语义探针：验证非法名单被严格隔离 (15分)
    # 因为不能简单用 not in (防 Agent 标注 "Rejected: Bob")，所以让大模型读懂语义
    exclusion_prompt = (
        "Check the report carefully. Ensure that Bob, David, and Frank (who requested invasive plants) "
        "are NOT listed as approved volunteers and their hours are NOT added to the valid total. "
        "Reply YES if they are completely excluded from the approved list, or NO if they are accidentally approved."
    )
    if has_files and llm_judge_content(exclusion_prompt, file_content):
        total_score += 15
        score_details.append({"item": "大模型校验 - 排除入侵植物申请者", "score": 15, "max_score": 15, "passed": True, "reason": "大模型判定入侵植物申请者已被正确剥离"})
    else:
        score_details.append({"item": "大模型校验 - 排除入侵植物申请者", "score": 0, "max_score": 15, "passed": False, "reason": "大模型发现报告中错误地批准了入侵植物申请者，或未将其严格剥离"})

    # 6. LLM 语义探针：报告格式与语气契合度 (15分)
    tone_prompt = (
        "Does this text look like a neat, coherent summary or report showing ONLY approved volunteer names "
        "and their total hours, fitting the persona of an introverted, eco-conscious organizer?"
    )
    if has_files and llm_judge_content(tone_prompt, file_content):
        total_score += 15
        score_details.append({"item": "大模型校验 - 报告规范性与 Persona 契合", "score": 15, "max_score": 15, "passed": True, "reason": "排版整洁，总结得当"})
    else:
        score_details.append({"item": "大模型校验 - 报告规范性与 Persona 契合", "score": 0, "max_score": 15, "passed": False, "reason": "未达到 Neat Summary 的要求或语气违和"})

    # 输出统一评测结果
    result_data = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=4, ensure_ascii=False)
        
    print(f"Verification finished. Total score: {total_score}")

if __name__ == "__main__":
    main()
