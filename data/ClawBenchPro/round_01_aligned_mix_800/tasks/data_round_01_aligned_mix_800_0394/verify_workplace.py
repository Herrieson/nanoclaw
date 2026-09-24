import os
import sys
import json
import re
import httpx
from openai import OpenAI

# ---------------------------------------------------------
# 1. 强制的 LLM 初始化与环境读取配置 (禁用 SSL 验证)
# ---------------------------------------------------------
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
    """大模型语义检测器，仅回答 YES/NO"""
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

# ---------------------------------------------------------
# 2. 核心验证逻辑
# ---------------------------------------------------------
def verify_workplace(workspace_path):
    score_details = []
    total_score = 0

    # 目标目录与文件检查
    target_dir = os.path.join(workspace_path, "for_mateo")
    output_files = []
    if os.path.exists(target_dir) and os.path.isdir(target_dir):
        output_files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
    
    # 【检测点 1】：目录结构与文件生成 (10分)
    if output_files:
        score_details.append({"item": "检查目标目录及文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 for_mateo 及文件已生成。"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标目录及文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 for_mateo 目录或目录下无文件。"})
        # 目录不存在直接写入 0 分并返回
        return write_result(0, score_details, workspace_path)

    # 读取最终生成的文件内容
    target_file = os.path.join(target_dir, output_files[0])
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception as e:
        score_details.append({"item": "读取最终生成文件", "score": 0, "max_score": 90, "passed": False, "reason": f"文件读取失败: {str(e)}"})
        return write_result(total_score, score_details, workspace_path)

    content_lower = content.lower()

    # 【检测点 2】：利用原生代码精确检测核心计算结果(Net Profit) (30分)
    # 逻辑: 1000 AC * 1.2 = 1200 USD. 餐饮 = 1300 USD. 总支出 = 2500 USD.
    # 总收入 = 800+450+1200+600+0+100+750 = 3900 USD. Net profit = 1400 USD.
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', content)
    if "1400" in numbers or "1400.00" in numbers:
        score_details.append({"item": "核对净利润数值的准确性", "score": 30, "max_score": 30, "passed": True, "reason": "精准提取到正确的净利润数值 (1400)。"})
        total_score += 30
    else:
        score_details.append({"item": "核对净利润数值的准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"文件内未找到正确的净利润 1400。提取到的数字有: {numbers}"})

    # 【检测点 3】：VIP 白名单精准包含校验 (20分)
    # 必须包含: Mr. Anderson, Julian Vance, Sophia Sterling
    required_names = ["mr. anderson", "julian vance", "sophia sterling"]
    missing_names = [name for name in required_names if name not in content_lower]
    if not missing_names:
        score_details.append({"item": "检查达标 VIP 名单完整性", "score": 20, "max_score": 20, "passed": True, "reason": "所有满足条件的 VIP 均在名单中。"})
        total_score += 20
    else:
        score_details.append({"item": "检查达标 VIP 名单完整性", "score": 0, "max_score": 20, "passed": False, "reason": f"遗漏了以下 VIP: {', '.join(missing_names)}"})

    # 【检测点 4】：严查幻觉与规则破坏 - 黑名单排除校验 (20分)
    # 绝不能包含: Isabella Torres(<=500), Marcus Reed(0), Lucia Gomez(Crasher>500), Crash Override(Crasher)
    forbidden_names = ["isabella", "marcus", "lucia", "override"]
    found_forbidden = [name for name in forbidden_names if name in content_lower]
    if not found_forbidden:
        score_details.append({"item": "严查非目标人员(Crasher/低消费)剔除情况", "score": 20, "max_score": 20, "passed": True, "reason": "未发现不合规人员，数据过滤逻辑严密。"})
        total_score += 20
    else:
        score_details.append({"item": "严查非目标人员(Crasher/低消费)剔除情况", "score": 0, "max_score": 20, "passed": False, "reason": f"严重违规，错误包含了不达标或非邀请人员: {', '.join(found_forbidden)}"})

    # 【检测点 5】：利用大模型检查自然语言的语义与行文语气 (20分)
    prompt = "Check if the following text reads like a polite list prepared for writing thank-you notes, and explicitly identifies the calculated number as the 'net profit' or similar financial context (not just a random number). Does it meet both criteria?"
    if llm_judge_content(prompt, content):
        score_details.append({"item": "LLM 语义验证: Thank-you list 格式与净利润语境", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定行文语气得当，且清晰标明了净利润含义。"})
        total_score += 20
    else:
        score_details.append({"item": "LLM 语义验证: Thank-you list 格式与净利润语境", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定文本语境缺失，仅为数据堆砌或未说明数字含义。"})

    return write_result(total_score, score_details, workspace_path)


def write_result(total_score, score_details, workspace_path):
    output_path = os.path.join(workspace_path, "workplace_score.json")
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Workplace evaluation complete. Score: {total_score}/100")
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
