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
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score_details = []
    total_score = 0
    
    # Check 1: Directory exists
    dir_exists = os.path.isdir(deliverables_dir)
    if dir_exists:
        total_score += 10
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
    else:
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        
    # Check 2: File exists
    file_content = ""
    file_exists = False
    if dir_exists:
        files = os.listdir(deliverables_dir)
        if files:
            file_exists = True
            total_score += 10
            score_details.append({"item": "检查 deliverables 目录下是否有文件", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
            # Read all files content
            for f in files:
                file_path = os.path.join(deliverables_dir, f)
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
                        file_content += fp.read() + "\n"
        else:
            score_details.append({"item": "检查 deliverables 目录下是否有文件", "score": 0, "max_score": 10, "passed": False, "reason": "目录为空"})
    else:
        score_details.append({"item": "检查 deliverables 目录下是否有文件", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})

    # Check 3-6: Content verification via LLM (if file exists)
    if file_exists and file_content.strip():
        # Check Rank 1
        q_rank1 = "Does this document explicitly recommend 'Aria_Style_Alpha' as one of the top valid influencers to hire?"
        if llm_judge_content(q_rank1, file_content):
            total_score += 20
            score_details.append({"item": "包含正确的第一名 Aria_Style_Alpha", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定包含了该人选"})
        else:
            score_details.append({"item": "包含正确的第一名 Aria_Style_Alpha", "score": 0, "max_score": 20, "passed": False, "reason": "未找到第一名推荐"})

        # Check Rank 2
        q_rank2 = "Does this document explicitly recommend 'Chemistry_Chloe_Beta' as one of the top valid influencers to hire?"
        if llm_judge_content(q_rank2, file_content):
            total_score += 20
            score_details.append({"item": "包含正确的第二名 Chemistry_Chloe_Beta", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定包含了该人选"})
        else:
            score_details.append({"item": "包含正确的第二名 Chemistry_Chloe_Beta", "score": 0, "max_score": 20, "passed": False, "reason": "未找到第二名推荐"})

        # Check Rank 3
        q_rank3 = "Does this document explicitly recommend 'Derma_Diana_Gamma' as one of the top valid influencers to hire?"
        if llm_judge_content(q_rank3, file_content):
            total_score += 20
            score_details.append({"item": "包含正确的第三名 Derma_Diana_Gamma", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定包含了该人选"})
        else:
            score_details.append({"item": "包含正确的第三名 Derma_Diana_Gamma", "score": 0, "max_score": 20, "passed": False, "reason": "未找到第三名推荐"})

        # Check Decoys
        q_decoys = "Does this document mistakenly recommend 'BioTech_Bob_Supreme' OR 'Scammy_Sam'? If it recommends either of them, say YES. If it correctly excludes them, say NO."
        if not llm_judge_content(q_decoys, file_content):
            total_score += 20
            score_details.append({"item": "未包含黑名单人员", "score": 20, "max_score": 20, "passed": True, "reason": "成功排除了被封禁的最高分选手"})
        else:
            score_details.append({"item": "未包含黑名单人员", "score": 0, "max_score": 20, "passed": False, "reason": "错误地包含了黑名单中的人员"})
    else:
        score_details.append({"item": "包含正确的第一名 Aria_Style_Alpha", "score": 0, "max_score": 20, "passed": False, "reason": "无文件内容"})
        score_details.append({"item": "包含正确的第二名 Chemistry_Chloe_Beta", "score": 0, "max_score": 20, "passed": False, "reason": "无文件内容"})
        score_details.append({"item": "包含正确的第三名 Derma_Diana_Gamma", "score": 0, "max_score": 20, "passed": False, "reason": "无文件内容"})
        score_details.append({"item": "未包含黑名单人员", "score": 0, "max_score": 20, "passed": False, "reason": "无文件内容"})

    # Output result
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
