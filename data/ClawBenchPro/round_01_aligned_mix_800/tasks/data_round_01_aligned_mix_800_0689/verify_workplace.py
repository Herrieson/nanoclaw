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
                {
                    "role": "system",
                    "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."
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
    deliverables_dir = os.path.join(workspace, "deliverables")

    details = []
    total_score = 0

    # 1. 检查 deliverables 目录是否存在
    if os.path.isdir(deliverables_dir):
        details.append({
            "item": "检查 deliverables 目录是否存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "deliverables 目录存在"
        })
        total_score += 10
    else:
        details.append({
            "item": "检查 deliverables 目录是否存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未找到 deliverables 目录"
        })

    # 2. 检查内部是否包含有效报告文件
    report_content = ""
    file_found = False
    if os.path.isdir(deliverables_dir):
        files = [f for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]
        if files:
            file_path = os.path.join(deliverables_dir, files[0])
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    report_content = f.read()
                
                if report_content.strip():
                    details.append({
                        "item": "检查 deliverables 目录下是否输出了非空报告",
                        "score": 10,
                        "max_score": 10,
                        "passed": True,
                        "reason": f"成功找到并读取文件: {files[0]}"
                    })
                    total_score += 10
                    file_found = True
                else:
                    details.append({
                        "item": "检查 deliverables 目录下是否输出了非空报告",
                        "score": 0,
                        "max_score": 10,
                        "passed": False,
                        "reason": f"文件 {files[0]} 内容为空"
                    })
            except Exception as e:
                details.append({
                    "item": "检查 deliverables 目录下是否输出了非空报告",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"读取文件失败: {e}"
                })
        else:
            details.append({
                "item": "检查 deliverables 目录下是否输出了非空报告",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "deliverables 目录下没有文件"
            })
    else:
        details.append({
            "item": "检查 deliverables 目录下是否输出了非空报告",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "目录不存在，无法检查文件"
        })

    # 3. 结构化数值代码严格解析（提取报告中所有的数字并进行确定性匹配）
    if file_found:
        numbers = []
        for match in re.findall(r'\b\d+(?:\.\d+)?\b', report_content):
            try:
                numbers.append(float(match))
            except ValueError:
                pass

        def check_number(name, val, score, reason_success):
            if any(abs(n - val) < 1e-6 for n in numbers):
                return {"item": name, "score": score, "max_score": score, "passed": True, "reason": reason_success}
            else:
                return {"item": name, "score": 0, "max_score": score, "passed": False, "reason": f"未在报告中匹配到精确数值: {val}"}

        res_19 = check_number("验证精确计算结果: Regular Eaters = 19", 19.0, 10, "准确计算出常规就餐人数为 19")
        details.append(res_19)
        total_score += res_19["score"]

        res_37 = check_number("验证精准购物需求: Tortillas = 37", 37.0, 10, "准备计算并输出了正确差额 37")
        details.append(res_37)
        total_score += res_37["score"]

        res_8 = check_number("验证精准购物需求: Chicken (lbs) = 8", 8.0, 10, "准确计算并输出了正确差额 8")
        details.append(res_8)
        total_score += res_8["score"]

        res_66 = check_number("验证精准购物需求: Cheese (oz) = 66", 66.0, 10, "准确计算并输出了正确差额 66")
        details.append(res_66)
        total_score += res_66["score"]

        res_275 = check_number("验证精准购物需求: Enchilada Sauce (cans) = 2.75", 2.75, 10, "准确计算并输出了正确小数差额 2.75")
        details.append(res_275)
        total_score += res_275["score"]

        # 4. 利用 LLM 验证非结构化文本的语气与结构
        prompt_prep = "Does the following document contain BOTH a clear 'shopping list' (ingredients to buy) AND a 'prep list' (or instructions for preparation)? Reply 'YES' if both are clearly presented, otherwise 'NO'."
        if llm_judge_content(prompt_prep, report_content):
            details.append({"item": "LLM 语义验证: 包含购物与准备双清单", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定同时包含两种清单"})
            total_score += 10
        else:
            details.append({"item": "LLM 语义验证: 包含购物与准备双清单", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定未完整包含两种清单"})

        prompt_tone = "Is the following document written in a strict, clear, and FORMAL tone? Reply 'YES' if the tone is highly professional, organized, and avoids excessive colloquialisms or personal panic. Reply 'NO' if it is informal or disorganized."
        if llm_judge_content(prompt_tone, report_content):
            details.append({"item": "LLM 语义验证: 报告语气是否正式 (Formal)", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定报告排版与语气正式清晰"})
            total_score += 20
        else:
            details.append({"item": "LLM 语义验证: 报告语气是否正式 (Formal)", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定报告语气不够正式或过于随意"})

    else:
        # 文件不存在时全部赋予0分
        for item_name, score in [
            ("验证精确计算结果: Regular Eaters = 19", 10),
            ("验证精准购物需求: Tortillas = 37", 10),
            ("验证精准购物需求: Chicken (lbs) = 8", 10),
            ("验证精准购物需求: Cheese (oz) = 66", 10),
            ("验证精准购物需求: Enchilada Sauce (cans) = 2.75", 10),
            ("LLM 语义验证: 包含购物与准备双清单", 10),
            ("LLM 语义验证: 报告语气是否正式 (Formal)", 20)
        ]:
            details.append({"item": item_name, "score": 0, "max_score": score, "passed": False, "reason": "报告文件不存在，跳过当前验证"})

    # 写入得分明细结果
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
