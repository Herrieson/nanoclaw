import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# 强制 API 规范：读取 MOCK 环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型统一检测接口：严格返回 YES/NO"""
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
    billing_dir = os.path.join(workspace, "billing_ready")
    csv_path = os.path.join(billing_dir, "clean_sessions.csv")
    txt_path = os.path.join(billing_dir, "summary.txt")

    score_details = []
    total_score = 0

    # 1. 结构与格式规范 (10分)
    if os.path.isdir(billing_dir) and os.path.isfile(csv_path) and os.path.isfile(txt_path):
        score_details.append({"item": "检查目标输出目录与文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "billing_ready 目录及两个输出文件均存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标输出目录与文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺失 billing_ready 目录或必需的输出文件"})

    # 2. 结构化数据：CSV 清洗与去重严格解析 (40分)
    # 不允许使用正则或大模型，必须通过 Python Data Structure 确保 100% 精确度
    if os.path.isfile(csv_path):
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = list(csv.reader(f))
            
            if len(reader) < 2:
                score_details.append({"item": "CSV结构与去重检查", "score": 0, "max_score": 15, "passed": False, "reason": "CSV 为空或缺少数据行"})
                score_details.append({"item": "CSV有效数据匹配度", "score": 0, "max_score": 25, "passed": False, "reason": "无法验证"})
            else:
                header = [h.strip().lower() for h in reader[0]]
                # 动态探寻列索引以提高鲁棒性
                date_idx, name_idx, code_idx, dur_idx = 0, 1, 2, 3
                for i, h in enumerate(header):
                    if "date" in h: date_idx = i
                    elif "patient" in h: name_idx = i
                    elif "code" in h: code_idx = i
                    elif "dur" in h or "hour" in h: dur_idx = i
                
                parsed_data = set()
                for r in reader[1:]:
                    if len(r) >= 4:
                        try:
                            date = r[date_idx].strip()
                            name = r[name_idx].strip().lower()
                            code = r[code_idx].strip()
                            hours = float(r[dur_idx].strip())
                            parsed_data.add((date, name, code, hours))
                        except (IndexError, ValueError):
                            continue
                
                # 验证目标集：精确包含去重且经过合法性检验的数据
                expected_data = {
                    ("2023-10-01", "miller, j.", "92507", 1.0),
                    ("2023-10-02", "smith, a.", "92521", 1.5),
                    ("2023-10-05", "wilson, k.", "92610", 1.0),
                    ("2023-10-10", "miller, j.", "92523", 2.0)
                }
                
                if len(reader[1:]) == 4 and len(parsed_data) == 4:
                    score_details.append({"item": "CSV结构与去重检查", "score": 15, "max_score": 15, "passed": True, "reason": "CSV 成功去除了带有脏字符的重复项，恰好保留 4 行唯一有效数据"})
                    total_score += 15
                else:
                    score_details.append({"item": "CSV结构与去重检查", "score": 0, "max_score": 15, "passed": False, "reason": f"预期有 4 条数据，实际检测到 {len(reader[1:])} 行，去重逻辑失败或遗漏数据"})

                if parsed_data == expected_data:
                    score_details.append({"item": "CSV有效数据匹配度", "score": 25, "max_score": 25, "passed": True, "reason": "CSV 剔除了无效的 88888 和 99999 代码记录，准确留存了白名单医疗服务"})
                    total_score += 25
                else:
                    score_details.append({"item": "CSV有效数据匹配度", "score": 0, "max_score": 25, "passed": False, "reason": "数据内容与标准的授权名单/会话详情未能完美匹配，可能存在未清理的非法代码"})
                    
        except Exception as e:
            score_details.append({"item": "CSV验证异常", "score": 0, "max_score": 40, "passed": False, "reason": f"解析CSV失败: {e}"})
    else:
        score_details.append({"item": "CSV结构与去重检查", "score": 0, "max_score": 15, "passed": False, "reason": "clean_sessions.csv 文件缺失"})
        score_details.append({"item": "CSV有效数据匹配度", "score": 0, "max_score": 25, "passed": False, "reason": "clean_sessions.csv 文件缺失"})

    # 3. 非结构化数据：使用 LLM 进行语义、数值提取与幻觉判断 (50分)
    if os.path.isfile(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                summary_content = f.read()
                
            # 测试用例 A: 精确数值检索
            prompt_hours = "Does this summary explicitly state that the total billable hours are exactly 5.5? Pay close attention to the number."
            if llm_judge_content(prompt_hours, summary_content):
                score_details.append({"item": "LLM语义检查：汇总有效计费工时", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定 Summary 中准确计算并输出了 5.5 个总计费工时"})
                total_score += 20
            else:
                score_details.append({"item": "LLM语义检查：汇总有效计费工时", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定 Summary 中未能明确指出 5.5 个总工时，计算错误或遗漏"})
                
            # 测试用例 B: 实体识别与幻觉抵抗
            prompt_denied = "Does this summary accurately identify the patients whose sessions could not be authorized (denied/unauthorized)? It MUST mention 'Brown' (or 'Brown, L.') AND 'Davis' (or 'Davis, M.'). It MUST NOT list any other patients as denied. Answer 'YES' only if both conditions are met."
            if llm_judge_content(prompt_denied, summary_content):
                score_details.append({"item": "LLM语义检查：拒绝授权的患者列表与幻觉排查", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定成功列出 Brown 和 Davis，且无额外捏造患者数据"})
                total_score += 30
            else:
                score_details.append({"item": "LLM语义检查：拒绝授权的患者列表与幻觉排查", "score": 0, "max_score": 30, "passed": False, "reason": "大模型判定拒绝患者列表错误、不完整，或出现了严重的幻觉数据"})
                
        except Exception as e:
            score_details.append({"item": "Summary 验证异常", "score": 0, "max_score": 50, "passed": False, "reason": f"读取或请求 LLM 失败: {e}"})
    else:
        score_details.append({"item": "LLM语义检查：汇总有效计费工时", "score": 0, "max_score": 20, "passed": False, "reason": "summary.txt 文件缺失"})
        score_details.append({"item": "LLM语义检查：拒绝授权的患者列表与幻觉排查", "score": 0, "max_score": 30, "passed": False, "reason": "summary.txt 文件缺失"})

    # 输出统一评测结果
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
