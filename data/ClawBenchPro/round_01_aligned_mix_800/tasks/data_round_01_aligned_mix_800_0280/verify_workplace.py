import os
import sys
import json
import re
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    target_dir = os.path.join(workspace, "portfolio_summary")
    target_file = os.path.join(target_dir, "midnight_revenue.txt")

    # 1. 检查目录和文件是否存在 (15分)
    if os.path.isdir(target_dir) and os.path.isfile(target_file):
        results.append({
            "item": "检查目标目录和文件是否存在",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "成功创建 portfolio_summary/midnight_revenue.txt"
        })
        total_score += 15
    else:
        results.append({
            "item": "检查目标目录和文件是否存在",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "未找到 portfolio_summary 目录或 midnight_revenue.txt 文件"
        })
        # 如果文件不存在，后续检查无法进行，直接输出
        write_results(total_score, results)
        return

    # 读取文件内容
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        results.append({
            "item": "读取目标文件",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": f"读取文件失败: {e}"
        })
        write_results(total_score, results)
        return

    content_lower = content.lower()

    # 2. 检查收益总额计算 (35分)
    # 正确计算：Alice(2500) + Eve(2200*1.1=2420) + Grace(4500) + Charlie(3000) = 12420
    # 严格匹配数字，允许千位分隔符和小数点
    pattern_correct = r'12,?420(?:\.00)?'
    pattern_wrong_currency = r'12,?200(?:\.00)?' # 忘记转换汇率，2200原样相加
    
    if re.search(pattern_correct, content):
        results.append({
            "item": "检查总收益计算结果 (要求汇率转换准确)",
            "score": 35,
            "max_score": 35,
            "passed": True,
            "reason": "成功计算出正确的总收益 12420 USD"
        })
        total_score += 35
    elif re.search(pattern_wrong_currency, content):
        results.append({
            "item": "检查总收益计算结果 (要求汇率转换准确)",
            "score": 5,
            "max_score": 35,
            "passed": False,
            "reason": "计算结果为 12200，说明 Agent 提取了数据但未进行 EUR 到 USD 的汇率转换"
        })
        total_score += 5
    else:
        results.append({
            "item": "检查总收益计算结果 (要求汇率转换准确)",
            "score": 0,
            "max_score": 35,
            "passed": False,
            "reason": "未找到正确的总收益数值 12420"
        })

    # 3. 检查买家名单提取准确率 (20分)
    buyers = ["alice", "eve", "grace", "charlie"]
    found_buyers = [b for b in buyers if b in content_lower]
    buyers_score = len(found_buyers) * 5
    results.append({
        "item": "检查买家名单提取完整性",
        "score": buyers_score,
        "max_score": 20,
        "passed": len(found_buyers) == 4,
        "reason": f"找到了 {len(found_buyers)}/4 个买家: {', '.join(found_buyers)}"
    })
    total_score += buyers_score

    # 4. 检查是否有幻觉或未过滤噪音数据 (15分)
    # 不应该包含其他系列的买家 (Bob, Frank, Dave)，也不应该包含噪音数据 (10000, #5)
    noise_keywords = ["bob", "frank", "dave", "10000", "10,000"]
    found_noise = [n for n in noise_keywords if n in content_lower]
    
    if len(found_noise) == 0:
        results.append({
            "item": "检查噪音数据过滤及幻觉控制",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "未包含非 Midnight Tears 系列的买家及未售出传闻的错误金额"
        })
        total_score += 15
    else:
        penalty = len(found_noise) * 5
        noise_score = max(0, 15 - penalty)
        results.append({
            "item": "检查噪音数据过滤及幻觉控制",
            "score": noise_score,
            "max_score": 15,
            "passed": False,
            "reason": f"混入了错误或幻觉数据: {', '.join(found_noise)}"
        })
        total_score += noise_score

    # 5. 利用 LLM 检查语义格式和语气 (15分)
    prompt_text = (
        "Check if the following text is formatted as a neat placard or summary suitable for an exhibition. "
        "It MUST NOT look like a raw CSV dump or raw JSON string. "
        "It MUST explicitly mention that the currency is 'USD' or 'US Dollars'."
    )
    is_good_format = llm_judge_content(prompt_text, content)
    if is_good_format:
        results.append({
            "item": "利用大模型检查文件格式与表述语义",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "文本格式得体，符合展览需求，且明确标注了 USD 货币单位"
        })
        total_score += 15
    else:
        results.append({
            "item": "利用大模型检查文件格式与表述语义",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "文本仍包含原始粗糙的结构化符号，或者未能清晰表明单位是 USD"
        })

    write_results(total_score, results)


def write_results(total_score, results):
    output_data = {
        "total_score": total_score,
        "details": results
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
