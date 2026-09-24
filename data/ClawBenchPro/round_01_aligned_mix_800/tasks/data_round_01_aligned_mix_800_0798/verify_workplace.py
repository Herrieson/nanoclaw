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
    """
    统一的非结构化语义与逻辑内容检测接口。
    用于审查由于格式、文件名自由带来的高维度评判。
    """
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
    
    total_score = 0
    details = []

    deliverables_path = os.path.join(workspace, "deliverables")
    
    # ==========================================
    # 1. 物理结构验证：目录与文件存在性 (20分)
    # ==========================================
    if os.path.isdir(deliverables_path):
        score = 10
        total_score += score
        details.append({
            "item": "检查目标目录是否存在", 
            "score": score, 
            "max_score": 10, 
            "passed": True, 
            "reason": "目录 'deliverables' 存在"
        })
    else:
        details.append({
            "item": "检查目标目录是否存在", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": "未找到要求的 'deliverables' 目录"
        })

    file_content = ""
    if os.path.isdir(deliverables_path):
        files = os.listdir(deliverables_path)
        if files:
            score = 10
            total_score += score
            details.append({
                "item": "检查目录下是否包含输出文件", 
                "score": score, 
                "max_score": 10, 
                "passed": True, 
                "reason": f"成功找到文件: {', '.join(files)}"
            })
            
            # 读取所有文件内容作为一个综合文本提供给 LLM 进行后续语义审计
            for f in files:
                f_path = os.path.join(deliverables_path, f)
                if os.path.isfile(f_path):
                    try:
                        with open(f_path, 'r', encoding='utf-8') as f_in:
                            file_content += f_in.read() + "\n\n"
                    except Exception:
                        pass
        else:
            details.append({
                "item": "检查目录下是否包含输出文件", 
                "score": 0, 
                "max_score": 10, 
                "passed": False, 
                "reason": "deliverables 目录存在，但没有任何文件"
            })
    else:
        details.append({
            "item": "检查目录下是否包含输出文件", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": "目标目录不存在，无法检查文件"
        })

    # ==========================================
    # 2. 语义与逻辑检测：LLM 复杂验证 (80分)
    # ==========================================
    if not file_content.strip():
        # 若物理文件不存在或无法读取，直接扣去所有内容分
        details.extend([
            {"item": "名单精准度验证", "score": 0, "max_score": 25, "passed": False, "reason": "无法读取文件，无法验证名单"},
            {"item": "目标食材完整度验证", "score": 0, "max_score": 25, "passed": False, "reason": "无法读取文件，无法验证食材"},
            {"item": "无关食材防误入验证", "score": 0, "max_score": 20, "passed": False, "reason": "无法读取文件，无法进行防幻觉检测"},
            {"item": "易读性及排版验证", "score": 0, "max_score": 10, "passed": False, "reason": "无法读取文件，无法验证排版"}
        ])
    else:
        # 2.1 名单精准度验证 (25分)
        # 必须是 Serving 且不是 Passed。符合的有 Mark Reyes, Pedro Cruz, Sarah Jenkins。
        prompt_servers = (
            "Check if the file explicitly identifies the unapproved/pending serving volunteers. "
            "The correct list must ONLY include exactly these three people: 'Mark Reyes', 'Pedro Cruz', and 'Sarah Jenkins'. "
            "It must NOT classify 'Ana Santos', 'Miguel Fernandez', 'John Doe', or 'Lucy Gomez' as unapproved servers. "
            "Reply YES if it identifies exactly the three correct people with no extra or missing names. Otherwise, reply NO."
        )
        if llm_judge_content(prompt_servers, file_content):
            total_score += 25
            details.append({"item": "名单精准度验证", "score": 25, "max_score": 25, "passed": True, "reason": "LLM 确认已准确提取出三名不合规的 Serving 志愿者，且无误报"})
        else:
            details.append({"item": "名单精准度验证", "score": 0, "max_score": 25, "passed": False, "reason": "LLM 判定名单提取有遗漏，或错误包含了其他志愿者/角色"})

        # 2.2 目标食材完整度验证 (25分)
        prompt_ingredients_in = (
            "Check if the grocery list contains the ingredients for all the 'Traditional Filipino' recipes. "
            "It must include items like Pork belly, Tamarind broth, Eggplant, Radish, Water spinach, Ground pork, "
            "Spring roll wrappers, Shaved ice, Ube halaya, Leche flan, Sweetened beans, etc. "
            "Reply YES if these Traditional Filipino ingredients are clearly and comprehensively present. Reply NO if they are significantly missing."
        )
        if llm_judge_content(prompt_ingredients_in, file_content):
            total_score += 25
            details.append({"item": "目标食材完整度验证", "score": 25, "max_score": 25, "passed": True, "reason": "LLM 确认菲律宾传统菜谱的核心配料均已被提取放入清单"})
        else:
            details.append({"item": "目标食材完整度验证", "score": 0, "max_score": 25, "passed": False, "reason": "LLM 判定有关键的传统菲律宾菜谱食材未被提取"})

        # 2.3 无关食材防误入验证 (20分)
        # 必须过滤掉 American 和 Italian 的菜谱
        prompt_ingredients_out = (
            "Check if the grocery list incorrectly includes ingredients for the American or Italian recipes. "
            "Look closely for words like: Macaroni, Cheddar, Milk (unless Evaporated milk), Butter, Pasta, Tomato sauce, Ground beef. "
            "Reply YES if the list is CLEAN and DOES NOT contain these unrelated ingredients. "
            "Reply NO if it mistakenly includes any of these."
        )
        if llm_judge_content(prompt_ingredients_out, file_content):
            total_score += 20
            details.append({"item": "无关食材防误入验证", "score": 20, "max_score": 20, "passed": True, "reason": "LLM 确认没有混入非菲律宾菜的配料(如意大利面、奶酪等)"})
        else:
            details.append({"item": "无关食材防误入验证", "score": 0, "max_score": 20, "passed": False, "reason": "LLM 判定清单中错误混入了美式或意式菜谱的配料"})

        # 2.4 易读性及排版验证 (10分)
        prompt_format = (
            "Check if the content is formatted as a clean, easy-to-read summary (e.g., using bullet points, clear headings, or organized lists). "
            "The user explicitly asked for something 'clear and easy to read on my screen' while grocery shopping. "
            "Reply YES if it is well-formatted. Reply NO if it is cluttered, unstructured, or hard to read."
        )
        if llm_judge_content(prompt_format, file_content):
            total_score += 10
            details.append({"item": "易读性及排版验证", "score": 10, "max_score": 10, "passed": True, "reason": "LLM 判定内容排版良好，具备适合手机阅读的摘要属性"})
        else:
            details.append({"item": "易读性及排版验证", "score": 0, "max_score": 10, "passed": False, "reason": "LLM 判定输出结果排版不佳，缺乏结构性"})

    # 输出结果
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
