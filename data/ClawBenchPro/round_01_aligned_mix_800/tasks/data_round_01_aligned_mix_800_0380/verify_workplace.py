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
    """
    统一的 LLM 语义检测接口。返回 True / False 
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

def write_score(score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)

def check_workplace(workspace):
    score = 0
    details = []
    
    target_dir = os.path.join(workspace, "finances_and_birds")
    
    # 1. 检查目标目录 (10分)
    if os.path.isdir(target_dir):
        score += 10
        details.append({"item": "检查目标目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建并找到了 finances_and_birds 目录"})
    else:
        details.append({"item": "检查目标目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到要求的 finances_and_birds 目录"})
        write_score(score, details)
        return

    # 2. 检查输出文件存在性 (10分)
    files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
    if not files:
        details.append({"item": "检查输出文件", "score": 0, "max_score": 10, "passed": False, "reason": "目标目录下是空的，没有生成总结文件"})
        write_score(score, details)
        return
        
    score += 10
    details.append({"item": "检查输出文件", "score": 10, "max_score": 10, "passed": True, "reason": f"找到输出文件数量: {len(files)}"})

    # 将目录下所有文件的内容合并为一个字符串以兼容多个文件的情形
    combined_content = ""
    for f in files:
        try:
            with open(os.path.join(target_dir, f), "r", encoding="utf-8") as file:
                combined_content += file.read() + "\n"
        except:
            pass

    content_lower = combined_content.lower()

    # 3. 检查总金额，前置代码扫描 + LLM 语义校验 (20分)
    # 计算公式：15(Sarah) + 22.50(John) + 8(Alice) + 12(Dave) = 57.50
    has_amount = bool(re.search(r'57\.50?', content_lower))
    if has_amount:
        prompt = "Does the text explicitly state that the total amount owed (or total unpaid sum) is exactly 57.5 or 57.50?"
        if llm_judge_content(prompt, combined_content):
            score += 20
            details.append({"item": "校验总欠款金额计算与语义", "score": 20, "max_score": 20, "passed": True, "reason": "精确找到 57.50，且 LLM 验证其具有'总欠款'的明确语义"})
        else:
            score += 10
            details.append({"item": "校验总欠款金额计算与语义", "score": 10, "max_score": 20, "passed": False, "reason": "文本中包含 57.50 的数值，但缺乏总欠款的结构/语义挂载"})
    else:
        details.append({"item": "校验总欠款金额计算与语义", "score": 0, "max_score": 20, "passed": False, "reason": "未在提取内容中找到准确的最终总金额 57.50 (可能计算错误)"})

    # 4. 检查欠款人名单 (20分)
    names = ["sarah", "john", "alice", "dave"]
    missing_names = [n for n in names if n not in content_lower]
    if not missing_names:
        prompt = "Does the text explicitly list Sarah, John, Alice, and Dave as the people who have unpaid debts or owe money?"
        if llm_judge_content(prompt, combined_content):
            score += 20
            details.append({"item": "检查欠款人实体提取准确性", "score": 20, "max_score": 20, "passed": True, "reason": "所有欠款人（Sarah, John, Alice, Dave）均被正确识别并语义定性"})
        else:
            score += 10
            details.append({"item": "检查欠款人实体提取准确性", "score": 10, "max_score": 20, "passed": False, "reason": "存在四个人的名字，但未能被 LLM 认定为'欠款人'，疑似数据混淆"})
    else:
        details.append({"item": "检查欠款人实体提取准确性", "score": 0, "max_score": 20, "passed": False, "reason": f"漏掉或误判了欠款人: {', '.join(missing_names)}"})

    # 5. 检查受调用Skill解析出的鸟类 (20分)
    birds = ["chickadee", "jay", "towhee", "cardinal"]
    missing_birds = [b for b in birds if b not in content_lower]
    if not missing_birds:
        prompt = "Does the text explicitly mention Black-capped Chickadee, Blue Jay, Eastern Towhee, and Northern Cardinal as bird species identified specifically by their calls?"
        if llm_judge_content(prompt, combined_content):
            score += 20
            details.append({"item": "检查基于专有技能产生的鸟类图鉴", "score": 20, "max_score": 20, "passed": True, "reason": "所有要求通过声学辨别的四种鸟类均被准确记录"})
        else:
            score += 10
            details.append({"item": "检查基于专有技能产生的鸟类图鉴", "score": 10, "max_score": 20, "passed": False, "reason": "找到了所有目标鸟类名字，但并未说明它们是通过叫声识别的"})
    else:
        details.append({"item": "检查基于专有技能产生的鸟类图鉴", "score": 0, "max_score": 20, "passed": False, "reason": f"未提取到所有的目标鸟类，缺少: {', '.join(missing_birds)}"})

    # 6. 检查信息去伪存真（防幻觉陷阱机制） (20分)
    # 诱导数据：Robin (看见但没听见叫声)、Mark (已付款)、Tom (已现金付款)
    has_trap_names = any(x in content_lower for x in ["mark", "tom", "robin"])
    if has_trap_names:
        prompt = "Does the text mistakenly list 'Mark' or 'Tom' as someone who STILL owes money, OR mistakenly list 'Robin' as a bird identified by its CALL? Answer YES if any of these mistakes are present."
        if llm_judge_content(prompt, combined_content):
            details.append({"item": "幻觉与数据干扰项排除检查", "score": 0, "max_score": 20, "passed": False, "reason": "触发一票否决：未能排除干扰数据（把已付款人列为欠款，或把只看见没听见叫声的Robin列入目标名单）"})
        else:
            score += 20
            details.append({"item": "幻觉与数据干扰项排除检查", "score": 20, "max_score": 20, "passed": True, "reason": "文本提及了陷阱对象(Robin/Mark/Tom)但进行了准确的条件排除声明"})
    else:
        score += 20
        details.append({"item": "幻觉与数据干扰项排除检查", "score": 20, "max_score": 20, "passed": True, "reason": "完美过滤了所有无效噪声，没有盲目抓取混淆数据"})

    write_score(score, details)

if __name__ == "__main__":
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    check_workplace(work_dir)
