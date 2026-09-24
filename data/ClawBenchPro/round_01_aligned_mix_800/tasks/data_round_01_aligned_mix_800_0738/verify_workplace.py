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
    
    family_archive_path = os.path.join(workspace, "family_archive.txt")
    junk_list_path = os.path.join(workspace, "junk_to_delete.txt")
    
    details = []
    total_score = 0
    
    # Check 1: family_archive.txt existence
    if os.path.exists(family_archive_path):
        details.append({"item": "检查 family_archive.txt 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
        with open(family_archive_path, 'r', encoding='utf-8') as f:
            archive_content = f.read()
    else:
        details.append({"item": "检查 family_archive.txt 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        archive_content = ""
        
    # Check 2: junk_to_delete.txt existence
    if os.path.exists(junk_list_path):
        details.append({"item": "检查 junk_to_delete.txt 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
        with open(junk_list_path, 'r', encoding='utf-8') as f:
            junk_content = f.read()
    else:
        details.append({"item": "检查 junk_to_delete.txt 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        junk_content = ""

    # Check 3: verify junk_to_delete.txt content (Exact string matches for filenames)
    expected_junks = [
        "math_hw_final.txt", "game_strats.md", "random_jokes.log", 
        "shopping_list.txt", "sys_error_881.log", "todo_weekend.txt"
    ]
    expected_traditionals = [
        "note_alpha.txt", "journal_33.log", "story_of_the_bear.md", "reflection.txt"
    ]
    
    if junk_content:
        junk_score = 0
        found_junks = []
        for j in expected_junks:
            if j in junk_content:
                junk_score += 5
                found_junks.append(j)
                
        # penalty for including traditional files
        penalty = 0
        for t in expected_traditionals:
            if t in junk_content:
                penalty += 5
                
        final_junk_score = max(0, junk_score - penalty)
        passed = final_junk_score == 30
        details.append({
            "item": "验证 junk_to_delete.txt 包含的垃圾文件名是否准确",
            "score": final_junk_score,
            "max_score": 30,
            "passed": passed,
            "reason": f"找到了 {len(found_junks)}/6 个垃圾文件。错误包含了 {penalty//5} 个重要文件。"
        })
        total_score += final_junk_score
    else:
        details.append({"item": "验证 junk_to_delete.txt 包含的垃圾文件名是否准确", "score": 0, "max_score": 30, "passed": False, "reason": "文件为空或不存在"})

    # Check 4: Verify family_archive.txt completeness and cleanliness via LLM
    if archive_content:
        traditions_checks = [
            ("是否包含了关于沙漠平静与阿帕奇祖先的描述？", "note_alpha.txt内容提取", 10),
            ("是否包含了 Auntie 的炸面包（frybread）食谱（面粉、泡打粉等）？", "journal_33.log内容提取", 10),
            ("是否包含了祖父讲述的关于熊的故事（平等、保护遗产）？", "story_of_the_bear.md内容提取", 10),
            ("是否包含了坐在窗边思考亚利桑那州传统仪式的反思？", "reflection.txt内容提取", 10)
        ]
        
        for prompt_q, name, weight in traditions_checks:
            passed = llm_judge_content(prompt_q, archive_content)
            if passed:
                details.append({"item": f"大模型验证 {name}", "score": weight, "max_score": weight, "passed": True, "reason": "验证通过"})
                total_score += weight
            else:
                details.append({"item": f"大模型验证 {name}", "score": 0, "max_score": weight, "passed": False, "reason": "缺失对应语义内容"})
                
        # Check 5: Cleanliness (No junk allowed)
        clean_prompt = "Did the file contain any irrelevant junk information such as algebra math problems, Fortnite/Elden Ring games, jokes about chickens, shopping lists with Doritos, or memory dump system errors? Answer 'YES' if it contains junk, 'NO' if it is clean."
        # If it answers NO, it means it is clean. We need a "YES" for our prompt to get boolean True.
        # Let's adjust the prompt to be positively aligned for our function:
        is_clean_prompt = "Is this file COMPLETELY FREE of any irrelevant junk information such as algebra/math problems, Fortnite/Elden Ring games, chicken jokes, junk food shopping lists, or system errors? Answer 'YES' if it is perfectly clean, 'NO' if any junk slipped in."
        is_clean = llm_judge_content(is_clean_prompt, archive_content)
        if is_clean:
            details.append({"item": "大模型验证 family_archive.txt 是否未被垃圾信息污染", "score": 10, "max_score": 10, "passed": True, "reason": "纯净无污染"})
            total_score += 10
        else:
            details.append({"item": "大模型验证 family_archive.txt 是否未被垃圾信息污染", "score": 0, "max_score": 10, "passed": False, "reason": "混入了垃圾文件内容"})
    else:
        details.append({"item": "大模型验证 family_archive.txt 的内容完整性与纯净度", "score": 0, "max_score": 50, "passed": False, "reason": "文件不存在或为空"})

    # Save score
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
