import os
import sys
import json
import httpx
from openai import OpenAI

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
    """使用大模型进行非结构化文本的严格语义检测"""
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
    resultados_dir = os.path.join(workspace, "resultados")
    
    score_details = []
    total_score = 0
    
    # 1. 结构化检测：目录是否存在 (10 分)
    dir_exists = os.path.isdir(resultados_dir)
    if dir_exists:
        score_details.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 resultados 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录 resultados 不存在"})
        
    # 2. 结构化检测：目录下是否有输出文档 (10 分)
    file_content = ""
    file_found = False
    if dir_exists:
        files = os.listdir(resultados_dir)
        valid_files = [f for f in files if os.path.isfile(os.path.join(resultados_dir, f))]
        if valid_files:
            file_found = True
            with open(os.path.join(resultados_dir, valid_files[0]), "r", encoding="utf-8") as f:
                file_content = f.read()
            score_details.append({"item": "检查是否生成了结果文档", "score": 10, "max_score": 10, "passed": True, "reason": f"找到了结果文件: {valid_files[0]}"})
            total_score += 10
        else:
            score_details.append({"item": "检查是否生成了结果文档", "score": 0, "max_score": 10, "passed": False, "reason": "resultados 目录下没有文件"})
    else:
        score_details.append({"item": "检查是否生成了结果文档", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在，无法检查文件"})
        
    # 3. 语义检测：利用 LLM 检查报废批次号 (40 分)
    if file_found and file_content.strip():
        # B103 (18%), B105 (16%), B108 (20%) 均为损坏批次。
        prompt_bad = (
            "Does the following text identify EXACTLY 'B103', 'B105', and 'B108' as the ruined/bad Cherry batches? "
            "It must contain ALL THREE of these IDs, and MUST NOT include any other IDs (such as B101, B102, B104, B106, B107, B109) as bad batches. "
            "Reply YES only if the bad batches are precisely B103, B105, and B108. Otherwise, reply NO."
        )
        if llm_judge_content(prompt_bad, file_content):
            score_details.append({"item": "准确识别报废的Cherry批次", "score": 40, "max_score": 40, "passed": True, "reason": "正确指出了所有且仅有 B103, B105, B108 为报废批次"})
            total_score += 40
        else:
            score_details.append({"item": "准确识别报废的Cherry批次", "score": 0, "max_score": 40, "passed": False, "reason": "报废批次识别遗漏、错误或包含了多余的批次（幻觉）"})
            
        # 4. 语义检测：利用 LLM 检查合格总升数 (40 分)
        # 合格Cherry: B101 (50L), B106 (200L), B107 (10L) -> 总体积 260L
        prompt_good = (
            "Does the following text explicitly state that the total volume of GOOD (or valid/leftover) Cherry stain is EXACTLY 260 liters (or just the number 260)? "
            "Reply YES only if the number 260 is explicitly stated as the total volume. If it calculates any other number, reply NO."
        )
        if llm_judge_content(prompt_good, file_content):
            score_details.append({"item": "准确计算合格Cherry批次的总剩余体积", "score": 40, "max_score": 40, "passed": True, "reason": "正确得出合格总体积为 260 升"})
            total_score += 40
        else:
            score_details.append({"item": "准确计算合格Cherry批次的总剩余体积", "score": 0, "max_score": 40, "passed": False, "reason": "合格总体积计算错误或未在文档中明确体现 260"})
    else:
        score_details.append({"item": "准确识别报废的Cherry批次", "score": 0, "max_score": 40, "passed": False, "reason": "没有找到结果文件或文件为空"})
        score_details.append({"item": "准确计算合格Cherry批次的总剩余体积", "score": 0, "max_score": 40, "passed": False, "reason": "没有找到结果文件或文件为空"})

    # 输出统一评分文件
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
