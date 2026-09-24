import os
import sys
import json
import httpx
from openai import OpenAI

# 强制规定的环境变量与客户端初始化
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """用于非结构化文本语义与数值提取的标准化 LLM 探针接口"""
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
    reports_dir = os.path.join(workspace, "reports")
    
    score_details = []
    total_score = 0
    
    # ====================================================================
    # 验证项 1: 报告目录结构验证 (代码实现，满分 10 分)
    # ====================================================================
    dir_exists = os.path.isdir(reports_dir)
    if dir_exists:
        score_details.append({"item": "检查 reports 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建了 reports 目录"})
        total_score += 10
    else:
        score_details.append({"item": "检查 reports 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 reports 目录"})
    
    # ====================================================================
    # 验证项 2: 报告文件存在性与内容读取 (代码实现，满分 10 分)
    # ====================================================================
    file_content = ""
    if dir_exists:
        files = [f for f in os.listdir(reports_dir) if os.path.isfile(os.path.join(reports_dir, f))]
        if len(files) > 0:
            score_details.append({"item": "检查 reports 目录下是否生成了总结文件", "score": 10, "max_score": 10, "passed": True, "reason": f"找到了文件: {files[0]}"})
            total_score += 10
            # 聚合读取所有生成的文件内容（通常只有1个）
            for file_name in files:
                try:
                    with open(os.path.join(reports_dir, file_name), "r", encoding="utf-8") as f:
                        file_content += f.read() + "\n"
                except:
                    pass
        else:
            score_details.append({"item": "检查 reports 目录下是否生成了总结文件", "score": 0, "max_score": 10, "passed": False, "reason": "reports 目录为空"})
    else:
        score_details.append({"item": "检查 reports 目录下是否生成了总结文件", "score": 0, "max_score": 10, "passed": False, "reason": "依赖的目录不存在"})

    # ====================================================================
    # LLM 语义验证区域 (满分 80 分) - 仅在文件内容存在时执行
    # ====================================================================
    if file_content.strip():
        # 验证项 3: 提取 Oxycodone 缺陷数量 (25 分)
        prompt_oxy = "Does the report explicitly state that 'Oxycodone' is missing exactly 5 pills (or has a deficit of 5)? Answer YES if it does."
        if llm_judge_content(prompt_oxy, file_content):
            score_details.append({"item": "准确计算并报告 Oxycodone 的亏空数量为 5", "score": 25, "max_score": 25, "passed": True, "reason": "大模型判定正确报告了 Oxycodone 的缺失数量"})
            total_score += 25
        else:
            score_details.append({"item": "准确计算并报告 Oxycodone 的亏空数量为 5", "score": 0, "max_score": 25, "passed": False, "reason": "未能在报告中正确找到 Oxycodone 缺失 5 粒的结论"})

        # 验证项 4: 提取 Adderall 缺陷数量 (25 分)
        prompt_add = "Does the report explicitly state that 'Adderall' is missing exactly 10 pills (or has a deficit of 10)? Answer YES if it does."
        if llm_judge_content(prompt_add, file_content):
            score_details.append({"item": "准确计算并报告 Adderall 的亏空数量为 10", "score": 25, "max_score": 25, "passed": True, "reason": "大模型判定正确报告了 Adderall 的缺失数量"})
            total_score += 25
        else:
            score_details.append({"item": "准确计算并报告 Adderall 的亏空数量为 10", "score": 0, "max_score": 25, "passed": False, "reason": "未能在报告中正确找到 Adderall 缺失 10 粒的结论"})

        # 验证项 5: 严惩幻觉与多余汇报项 (20 分)
        prompt_exclude = "The user strictly asked ONLY for drugs that are missing pills. Does the report STRICTLY EXCLUDE drugs that are perfectly balanced (specifically: Amoxicillin, Lisinopril, Diazepam, Ibuprofen)? Answer YES only if these drugs are completely absent from the final missing summary list."
        if llm_judge_content(prompt_exclude, file_content):
            score_details.append({"item": "严格按照要求剔除了库存平衡的药物", "score": 20, "max_score": 20, "passed": True, "reason": "未在报告中发现不符合要求的冗余药物信息"})
            total_score += 20
        else:
            score_details.append({"item": "严格按照要求剔除了库存平衡的药物", "score": 0, "max_score": 20, "passed": False, "reason": "报告违反要求，包含了库存平衡的药物名称"})

        # 验证项 6: 检查正式程度 (10 分)
        prompt_format = "Is this text written as a formal summary or professional report? (e.g. not a JSON dump, not a code snippet, but a formal written text/list). Answer YES if it looks like a formal summary."
        if llm_judge_content(prompt_format, file_content):
            score_details.append({"item": "报告格式符合正式总结的要求", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定输出内容符合正式总结基调"})
            total_score += 10
        else:
            score_details.append({"item": "报告格式符合正式总结的要求", "score": 0, "max_score": 10, "passed": False, "reason": "输出格式过于粗糙（如仅抛出 JSON 代码等）"})
    else:
        # 如果文件为空或不存在，LLM部分全部给 0 分
        score_details.extend([
            {"item": "准确计算并报告 Oxycodone 的亏空数量为 5", "score": 0, "max_score": 25, "passed": False, "reason": "未找到有效的文件内容"},
            {"item": "准确计算并报告 Adderall 的亏空数量为 10", "score": 0, "max_score": 25, "passed": False, "reason": "未找到有效的文件内容"},
            {"item": "严格按照要求剔除了库存平衡的药物", "score": 0, "max_score": 20, "passed": False, "reason": "未找到有效的文件内容"},
            {"item": "报告格式符合正式总结的要求", "score": 0, "max_score": 10, "passed": False, "reason": "未找到有效的文件内容"}
        ])

    # 结果落地
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
