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
    """使用大模型检测非结构化文本内容"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a strict data validation assistant. You evaluate reports. Answer ONLY with 'YES' or 'NO'."
                },
                {
                    "role": "user", 
                    "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"
                }
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
    
    summary_dir = os.path.join(workspace, "summary")
    
    # ==========================================
    # 1. 物理目录与文件检查 (10分)
    # ==========================================
    if os.path.exists(summary_dir) and os.path.isdir(summary_dir):
        files = [f for f in os.listdir(summary_dir) if os.path.isfile(os.path.join(summary_dir, f))]
        if len(files) > 0:
            score_details.append({
                "item": "检查报告文件是否存在", 
                "score": 10, "max_score": 10, "passed": True, 
                "reason": f"summary 目录下找到 {len(files)} 个文件。"
            })
            total_score += 10
            
            # 读取所有报告内容合并用于后续语义分析
            report_content = ""
            for fname in files:
                filepath = os.path.join(summary_dir, fname)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        report_content += f"\n--- {fname} ---\n" + f.read()
                except Exception as e:
                    pass
        else:
            score_details.append({
                "item": "检查报告文件是否存在", 
                "score": 0, "max_score": 10, "passed": False, 
                "reason": "summary 目录存在但为空，没有生成报告。"
            })
            report_content = None
    else:
        score_details.append({
            "item": "检查报告文件是否存在", 
            "score": 0, "max_score": 10, "passed": False, 
            "reason": "summary 目录不存在，未生成报告。"
        })
        report_content = None

    # 如果有内容，则进行后续 LLM 探针检测
    if report_content:
        # ==========================================
        # 2. 检查总工时计算准确性 (30分)
        # ==========================================
        prompt_hours = (
            "Does the report explicitly state that the TOTAL service/contribution hours for the "
            "officially whitelisted volunteers is exactly 22.5 (or 22.5 hours)?\n"
            "Criteria for 'YES': The exact number 22.5 must be mentioned and attributed as the total "
            "hours for the valid/whitelist volunteers."
        )
        if llm_judge_content(prompt_hours, report_content):
            score_details.append({
                "item": "利用大模型检查白名单总工时是否正确计算为 22.5 小时", 
                "score": 30, "max_score": 30, "passed": True, 
                "reason": "报告中准确指出了白名单总工时为 22.5。"
            })
            total_score += 30
        else:
            score_details.append({
                "item": "利用大模型检查白名单总工时是否正确计算为 22.5 小时", 
                "score": 0, "max_score": 30, "passed": False, 
                "reason": "未能准确指出白名单总工时为 22.5，或数值错误（应为佐藤4+2,田中3.5,铃木5,高桥2,渡边6）。"
            })

        # ==========================================
        # 3. 检查闯入者提取 (30分)
        # ==========================================
        prompt_intruders = (
            "Does the report explicitly identify exactly these three entities as intruders/unauthorized/non-whitelisted "
            "people: 'Ghost In Shell', 'Madara Uchiha', and 'Aizen Sosuke'?\n"
            "Criteria for 'YES': All three names (or very close variants) must be listed as intruders or not on the whitelist."
        )
        if llm_judge_content(prompt_intruders, report_content):
            score_details.append({
                "item": "利用大模型检查闯入者名单是否找全", 
                "score": 30, "max_score": 30, "passed": True, 
                "reason": "准确找出了Ghost In Shell, Madara Uchiha, Aizen Sosuke 三位非白名单成员。"
            })
            total_score += 30
        else:
            score_details.append({
                "item": "利用大模型检查闯入者名单是否找全", 
                "score": 0, "max_score": 30, "passed": False, 
                "reason": "未找全或找错了闯入者名单，未排除白名单成员。"
            })

        # ==========================================
        # 4. 检查动漫角色鉴定结果 (30分)
        # ==========================================
        prompt_anime = (
            "Does the report clearly state that the intruders ('Ghost In Shell', 'Madara Uchiha', 'Aizen Sosuke') "
            "are Anime/Manga characters, Otaku culture references, or fictitious names?\n"
            "Criteria for 'YES': The report must mention their anime/manga/fictional identities based on a search tool."
        )
        if llm_judge_content(prompt_anime, report_content):
            score_details.append({
                "item": "利用大模型检查动漫角色属性鉴定", 
                "score": 30, "max_score": 30, "passed": True, 
                "reason": "报告中指明了这三者的二次元/动漫角色属性。"
            })
            total_score += 30
        else:
            score_details.append({
                "item": "利用大模型检查动漫角色属性鉴定", 
                "score": 0, "max_score": 30, "passed": False, 
                "reason": "报告未包含或未能正确说明这些闯入者名字是动漫角色。"
            })
    else:
        # 如果没有文件，后面的LLM检测全部按 0 分记
        for desc, m_score in [("检查总工时计算(22.5)", 30), ("检查闯入者名单", 30), ("检查动漫属性鉴定", 30)]:
            score_details.append({
                "item": f"利用大模型{desc}", 
                "score": 0, "max_score": m_score, "passed": False, 
                "reason": "报告文件不存在，跳过验证。"
            })

    # 结果写入 workplace_score.json
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

    print(f"Workplace verification completed. Total Score: {total_score}/100")

if __name__ == "__main__":
    main()
