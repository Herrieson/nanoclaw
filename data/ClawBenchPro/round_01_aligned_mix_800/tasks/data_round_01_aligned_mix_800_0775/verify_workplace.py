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
    reports_dir = os.path.join(workspace, "reports")
    
    details = []
    total_score = 0
    
    # 1. 结构化代码检测：检查 reports 目录是否存在 (10分)
    if os.path.isdir(reports_dir):
        details.append({"item": "检查 reports 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "reports 目录已成功创建"})
        total_score += 10
    else:
        details.append({"item": "检查 reports 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 reports 目录"})
        
    # 2. 结构化代码检测：检查 reports 目录下是否有摘要文件 (10分)
    content = ""
    has_file = False
    if os.path.isdir(reports_dir):
        files = [f for f in os.listdir(reports_dir) if os.path.isfile(os.path.join(reports_dir, f))]
        if files:
            has_file = True
            details.append({"item": "检查 reports 目录下是否有生成文件", "score": 10, "max_score": 10, "passed": True, "reason": f"找到文件: {', '.join(files)}"})
            total_score += 10
            # 安全聚合文件内容
            for f in files:
                try:
                    with open(os.path.join(reports_dir, f), "r", encoding="utf-8") as file_obj:
                        content += file_obj.read() + "\n"
                except Exception as e:
                    pass
        else:
            details.append({"item": "检查 reports 目录下是否有生成文件", "score": 0, "max_score": 10, "passed": False, "reason": "reports 目录下为空，Agent未写入任何摘要"})
    else:
        details.append({"item": "检查 reports 目录下是否有生成文件", "score": 0, "max_score": 10, "passed": False, "reason": "reports 目录不存在，无法进行文件检查"})
        
    # 3. 确定性代码过滤与防作弊：严厉杜绝平衡药物被列出 (20分)
    # 不依赖模型判断，直接使用代码做强过滤，发现捏造或者啰嗦一票否决
    if has_file and content.strip():
        content_lower = content.lower()
        # 这些是帐实相符，不该出现在报告中的药物
        balanced_drugs = ["amoxicillin", "lisinopril", "diazepam", "ibuprofen"]
        found_balanced = [drug for drug in balanced_drugs if drug in content_lower]
        if not found_balanced:
            details.append({"item": "严格确保摘要未包含任何处于平衡状态的药物", "score": 20, "max_score": 20, "passed": True, "reason": "通过代码排查，未提及任何无缺失的药物"})
            total_score += 20
        else:
            details.append({"item": "严格确保摘要未包含任何处于平衡状态的药物", "score": 0, "max_score": 20, "passed": False, "reason": f"一票否决：发现了不应出现在缺失报告中的药物: {', '.join(found_balanced)}"})
    else:
        details.append({"item": "严格确保摘要未包含任何处于平衡状态的药物", "score": 0, "max_score": 20, "passed": False, "reason": "无文件内容可供验证"})

    # 4. LLM 语义检测：Oxycodone 精准缺失量计算 (20分)
    if has_file and content.strip():
        prompt = "Does the file content explicitly state that the drug 'Oxycodone' is missing exactly 5 pills (or units)? Answer YES if it strictly says 5 for Oxycodone, otherwise NO."
        if llm_judge_content(prompt, content):
            details.append({"item": "利用大模型检查是否准确报告 Oxycodone 缺失数量为 5", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定正确包含 Oxycodone 缺失 5 的信息"})
            total_score += 20
        else:
            details.append({"item": "利用大模型检查是否准确报告 Oxycodone 缺失数量为 5", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定未报告 Oxycodone 的准确缺失量或数字错误"})
    else:
        details.append({"item": "利用大模型检查是否准确报告 Oxycodone 缺失数量为 5", "score": 0, "max_score": 20, "passed": False, "reason": "无文件内容"})

    # 5. LLM 语义检测：Adderall 精准缺失量计算 (20分)
    if has_file and content.strip():
        prompt = "Does the file content explicitly state that the drug 'Adderall' is missing exactly 10 pills (or units)? Answer YES if it strictly says 10 for Adderall, otherwise NO."
        if llm_judge_content(prompt, content):
            details.append({"item": "利用大模型检查是否准确报告 Adderall 缺失数量为 10", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定正确包含 Adderall 缺失 10 的信息"})
            total_score += 20
        else:
            details.append({"item": "利用大模型检查是否准确报告 Adderall 缺失数量为 10", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定未报告 Adderall 的准确缺失量或数字错误"})
    else:
        details.append({"item": "利用大模型检查是否准确报告 Adderall 缺失数量为 10", "score": 0, "max_score": 20, "passed": False, "reason": "无文件内容"})

    # 6. LLM 语义检测：正式专业语气防乱码与终端日志 (20分)
    if has_file and content.strip():
        prompt = "Is the file content presented as a formal and professional summary suitable for management, focusing STRICTLY on the deficit without messy terminal outputs, redundant logs, or raw code snippets? Reply YES or NO."
        if llm_judge_content(prompt, content):
            details.append({"item": "检查摘要语气是否正式专业且无控制台杂讯", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定摘要格式正式，适合汇报"})
            total_score += 20
        else:
            details.append({"item": "检查摘要语气是否正式专业且无控制台杂讯", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定摘要包含杂讯、啰嗦日志或语气不够正式"})
    else:
        details.append({"item": "检查摘要语气是否正式专业且无控制台杂讯", "score": 0, "max_score": 20, "passed": False, "reason": "无文件内容"})
        
    # 保存结果
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
