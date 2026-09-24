import os
import sys
import json
import httpx
from openai import OpenAI

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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    planning_dir = os.path.join(workspace, "planning_docs")
    
    # 1. Check if the required directory exists
    if os.path.isdir(planning_dir):
        score_details.append({"item": "检查 planning_docs 目录是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "规划文档目录存在"})
        total_score += 20
    else:
        score_details.append({"item": "检查 planning_docs 目录是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 planning_docs 目录"})
        
    # 2. Check if a summary file was generated inside the directory
    content = ""
    if os.path.isdir(planning_dir):
        files = os.listdir(planning_dir)
        if len(files) > 0:
            score_details.append({"item": "检查 planning_docs 目录下是否有总结文件", "score": 10, "max_score": 10, "passed": True, "reason": "成功输出总结文件"})
            total_score += 10
            for f in files:
                file_path = os.path.join(planning_dir, f)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            content += file.read() + "\n"
                    except Exception as e:
                        pass
        else:
            score_details.append({"item": "检查 planning_docs 目录下是否有总结文件", "score": 0, "max_score": 10, "passed": False, "reason": "规划文档目录为空，无总结文件"})
    else:
        score_details.append({"item": "检查 planning_docs 目录下是否有总结文件", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在，无法检查文件"})
        
    # 3. LLM semantic checks for unstructured output content
    if content.strip():
        # A. Check correct total valid hours explicitly
        prompt_hours = "Does the document clearly state that the total combined valid hours offered by the qualified volunteers is exactly 23? Answer YES only if the number 23 is explicitly mentioned as the total valid hours."
        if llm_judge_content(prompt_hours, content):
            score_details.append({"item": "大模型校验: 验证总有效时长是否精确计算为 23 小时", "score": 30, "max_score": 30, "passed": True, "reason": "文档正确指出了有效的总服务时长为 23 小时（成功过滤脏数据和负数）"})
            total_score += 30
        else:
            score_details.append({"item": "大模型校验: 验证总有效时长是否精确计算为 23 小时", "score": 0, "max_score": 30, "passed": False, "reason": "未能准确计算并输出总服务时长为 23 小时，可能未排除脏数据"})
            
        # B. Check correct inclusion of qualified candidates
        prompt_names = "Does the document explicitly list or mention 'John Doe', 'Maria Garcia', 'Tom Smith', and 'David Kim' as the qualified individuals? Answer YES only if all four of these exact names are included in the summary."
        if llm_judge_content(prompt_names, content):
            score_details.append({"item": "大模型校验: 检查持证合格志愿者名单完整性", "score": 30, "max_score": 30, "passed": True, "reason": "包含所有四名具备目标资质且提供有效时间的志愿者"})
            total_score += 30
        else:
            score_details.append({"item": "大模型校验: 检查持证合格志愿者名单完整性", "score": 0, "max_score": 30, "passed": False, "reason": "合格志愿者名单不完整或存在遗漏"})
            
        # C. Check exclusion of unqualified candidates
        prompt_exclude = "Are 'Alex P', 'Zack W', and 'Linda B' correctly excluded from the qualified list? Answer YES if they are NOT mentioned as qualified (they can be completely omitted or mentioned specifically as unqualified)."
        if llm_judge_content(prompt_exclude, content):
            score_details.append({"item": "大模型校验: 检查未合格人员是否被正确排除", "score": 10, "max_score": 10, "passed": True, "reason": "完美排除了未获得指定资质的干扰人员"})
            total_score += 10
        else:
            score_details.append({"item": "大模型校验: 检查未合格人员是否被正确排除", "score": 0, "max_score": 10, "passed": False, "reason": "错误地将未合格人员（Alex P, Zack W, Linda B）列入了合格名单中"})
            
    else:
        score_details.append({"item": "大模型校验: 验证总有效时长是否精确计算为 23 小时", "score": 0, "max_score": 30, "passed": False, "reason": "无文件内容，无法验证时长"})
        score_details.append({"item": "大模型校验: 检查持证合格志愿者名单完整性", "score": 0, "max_score": 30, "passed": False, "reason": "无文件内容，无法验证人员名单"})
        score_details.append({"item": "大模型校验: 检查未合格人员是否被正确排除", "score": 0, "max_score": 10, "passed": False, "reason": "无文件内容，无法验证人员排除情况"})

    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
