import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# 强制 API 规范：从环境变量读取配置
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
    """用于检测非结构化文本/半结构化格式冗余的统一接口"""
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
    details = []
    total_score = 0
    
    # --- 1. 检查目标目录 (10分) ---
    deliverables_dir = os.path.join(workspace, "deliverables")
    if os.path.isdir(deliverables_dir):
        details.append({"item": "检查交付目录", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables 目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查交付目录", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录缺失"})
    
    # --- 2. 检查 CSV 报告 (50分) ---
    csv_path = os.path.join(deliverables_dir, "math_assessment_summary.csv")
    if os.path.isfile(csv_path):
        details.append({"item": "检查CSV报告存在性", "score": 5, "max_score": 5, "passed": True, "reason": "math_assessment_summary.csv 存在"})
        total_score += 5
        
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = [h.strip() for h in next(reader)]
                
                # 检查表头 (10分)
                if headers == ["official_name", "total_time_spent", "average_math_score"]:
                    details.append({"item": "检查CSV表头格式", "score": 10, "max_score": 10, "passed": True, "reason": "CSV表头完全正确"})
                    total_score += 10
                else:
                    details.append({"item": "检查CSV表头格式", "score": 0, "max_score": 10, "passed": False, "reason": f"表头不符合预期，实际为 {headers}"})
                
                # 解析行数据
                rows = list(reader)
                parsed_data = {}
                for r in rows:
                    if len(r) == 3:
                        try:
                            parsed_data[r[0].strip().lower()] = (float(r[1]), float(r[2]))
                        except ValueError:
                            pass # 忽略无法转换为浮点数的数据
                
                # 检查过滤逻辑：未参加Math的 Chloe Smith 是否被错误包含 (10分)
                if "chloe smith" in parsed_data:
                    details.append({"item": "检查过滤逻辑(未参加者)", "score": 0, "max_score": 10, "passed": False, "reason": "未参加math的 Chloe Smith 被错误包含在报告中"})
                else:
                    details.append({"item": "检查过滤逻辑(未参加者)", "score": 10, "max_score": 10, "passed": True, "reason": "成功剔除未参加math的学生"})
                    total_score += 10
                    
                # 检查数据精确计算 (25分)
                expected_data = {
                    "leo rossi": (55.0, 82.5),
                    "mia wong": (35.0, 62.5),
                    "robert brown": (50.0, 95.0),
                    "emily chen": (25.0, 90.0)
                }
                
                row_score = 0
                all_matched = True
                for name, (exp_time, exp_score) in expected_data.items():
                    if name in parsed_data:
                        act_time, act_score = parsed_data[name]
                        if abs(act_time - exp_time) < 0.1 and abs(act_score - exp_score) < 0.1:
                            row_score += 5
                        else:
                            all_matched = False
                    else:
                        all_matched = False
                
                # 满分加成（如果没有幻觉额外的人员）
                if all_matched and len(parsed_data) == 4:
                    row_score += 5 
                    details.append({"item": "检查CSV数据准确性", "score": 25, "max_score": 25, "passed": True, "reason": "所有学生的计算数据均精准无误，且无幻觉人员"})
                    total_score += 25
                else:
                    details.append({"item": "检查CSV数据准确性", "score": row_score, "max_score": 25, "passed": False, "reason": f"部分数据计算错误或人员缺失。部分得分 {row_score}"})
                    total_score += row_score

        except Exception as e:
            details.append({"item": "解析CSV文件异常", "score": 0, "max_score": 45, "passed": False, "reason": f"解析/校验结构化CSV时崩溃: {e}"})
    else:
        details.append({"item": "检查CSV报告存在性", "score": 0, "max_score": 50, "passed": False, "reason": "CSV报告缺失，该板块得分为0"})

    # --- 3. 检查 struggling_students.txt (40分) ---
    txt_path = os.path.join(deliverables_dir, "struggling_students.txt")
    if os.path.isfile(txt_path):
        details.append({"item": "检查 struggling_students 存在性", "score": 5, "max_score": 5, "passed": True, "reason": "TXT文件存在"})
        total_score += 5
        
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            
            # Agent 有时在 txt 里会添加冗余对话，或者严格遵循 "one per line"
            if len(lines) == 2 and set(lines) == {"Mia Wong", "Emily Chen"}:
                details.append({"item": "检查 struggling_students 语义内容", "score": 35, "max_score": 35, "passed": True, "reason": "精准输出两人名单，格式完美 (one per line)"})
                total_score += 35
            else:
                # 当非完美格式时，启用 LLM 探针以验证半结构化文本是否语义合规
                prompt = (
                    "Check if the following text is intended to ONLY list 'Mia Wong' and 'Emily Chen' as struggling students. "
                    "It might contain conversational fluff (like 'Here is the list:'), bullet points, or numbers. "
                    "However, if it hallucinated and listed any OTHER official names (e.g., Leo Rossi, Robert Brown, Chloe Smith), "
                    "or missed one of the two targets, you MUST answer NO. "
                    "If it accurately conveys JUST 'Mia Wong' and 'Emily Chen' despite formatting flaws, answer YES."
                )
                if llm_judge_content(prompt, content):
                    details.append({"item": "检查 struggling_students 语义内容", "score": 20, "max_score": 35, "passed": False, "reason": "LLM 判定找出了正确名单，但包含了废话或未遵循严谨格式，酌情给分"})
                    total_score += 20
                else:
                    details.append({"item": "检查 struggling_students 语义内容", "score": 0, "max_score": 35, "passed": False, "reason": "逻辑计算错误，找错人，或严重幻觉"})
                    
        except Exception as e:
            details.append({"item": "解析TXT文件异常", "score": 0, "max_score": 35, "passed": False, "reason": f"TXT读取失败: {e}"})
    else:
        details.append({"item": "检查 struggling_students 存在性", "score": 0, "max_score": 40, "passed": False, "reason": "TXT文件缺失，该板块得分为0"})
        
    # --- 最终输出结果 ---
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=4)

if __name__ == "__main__":
    verify()
