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
    report_file = os.path.join(workspace, "parent_reports", "safe_garden_snacks.json")
    
    total_score = 0
    details = []
    
    # ---------------------------------------------------------
    # 1. 物理目录与文件探针 (10分)
    # ---------------------------------------------------------
    report_dir = os.path.dirname(report_file)
    if os.path.exists(report_dir):
        details.append({"item": "检查目标目录 parent_reports 是否存在", "score": 2, "max_score": 2, "passed": True, "reason": "目录存在"})
        total_score += 2
    else:
        details.append({"item": "检查目标目录 parent_reports 是否存在", "score": 0, "max_score": 2, "passed": False, "reason": "目录不存在"})
        
    if os.path.exists(report_file):
        details.append({"item": "检查目标文件 safe_garden_snacks.json 是否存在", "score": 8, "max_score": 8, "passed": True, "reason": "文件存在"})
        total_score += 8
    else:
        details.append({"item": "检查目标文件 safe_garden_snacks.json 是否存在", "score": 0, "max_score": 8, "passed": False, "reason": "文件不存在"})
        # 如果文件不存在，直接熔断退出并输出 0-10 之间的当前分
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # ---------------------------------------------------------
    # 2. 严格结构化与类型验证 (10分)
    # ---------------------------------------------------------
    try:
        with open(report_file, "r") as f:
            data = json.load(f)
        details.append({"item": "文件是否为合法 JSON", "score": 8, "max_score": 8, "passed": True, "reason": "成功解析为 JSON"})
        total_score += 8
        
        if isinstance(data, dict):
            details.append({"item": "JSON 根节点是否为字典结构", "score": 2, "max_score": 2, "passed": True, "reason": "根节点是合法的键值对映射"})
            total_score += 2
        else:
            details.append({"item": "JSON 根节点是否为字典结构", "score": 0, "max_score": 2, "passed": False, "reason": "根节点不是字典对象，不符合 mapping 要求"})
            with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
                json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
            return
            
    except Exception as e:
        details.append({"item": "文件是否为合法 JSON", "score": 0, "max_score": 8, "passed": False, "reason": f"解析失败: {str(e)}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # ---------------------------------------------------------
    # 3. 核心数据解析: Target 1 (Noah) - 严格相等验证 (20分)
    # ---------------------------------------------------------
    noah_snack = data.get("Noah", "")
    if noah_snack and "celery sticks" in str(noah_snack).lower():
        details.append({"item": "是否精确提取 Noah 的零食 (Celery Sticks)", "score": 20, "max_score": 20, "passed": True, "reason": "精准包含对应零食数据"})
        total_score += 20
    else:
        details.append({"item": "是否精确提取 Noah 的零食 (Celery Sticks)", "score": 0, "max_score": 20, "passed": False, "reason": f"未提取或获取错误，当前值为: {noah_snack}"})

    # ---------------------------------------------------------
    # 4. 核心数据解析: Target 2 (Chloe) - 严格相等验证 (20分)
    # ---------------------------------------------------------
    chloe_snack = data.get("Chloe", "")
    if chloe_snack and "carrot sticks" in str(chloe_snack).lower():
        details.append({"item": "是否精确提取 Chloe 的零食 (Carrot Sticks)", "score": 20, "max_score": 20, "passed": True, "reason": "精准包含对应零食数据"})
        total_score += 20
    else:
        details.append({"item": "是否精确提取 Chloe 的零食 (Carrot Sticks)", "score": 0, "max_score": 20, "passed": False, "reason": f"未提取或获取错误，当前值为: {chloe_snack}"})

    # ---------------------------------------------------------
    # 5. 反向作弊与逻辑混淆检测: 剔除无过敏儿童 (10分)
    # ---------------------------------------------------------
    if "Emma" not in data:
        details.append({"item": "正确剔除无过敏儿童 (Emma)", "score": 10, "max_score": 10, "passed": True, "reason": "成功排除了 allergy=None 的儿童，未发生假阳性"})
        total_score += 10
    else:
        details.append({"item": "正确剔除无过敏儿童 (Emma)", "score": 0, "max_score": 10, "passed": False, "reason": "逻辑漏洞: 错误包含了无过敏儿童 Emma"})

    # ---------------------------------------------------------
    # 6. 反向作弊与逻辑混淆检测: 剔除错误活动儿童 (10分)
    # ---------------------------------------------------------
    if "Liam" not in data and "Mason" not in data:
        details.append({"item": "正确剔除未参与花园活动的儿童 (Liam, Mason)", "score": 10, "max_score": 10, "passed": True, "reason": "成功排除了室内阅读和睡觉的儿童"})
        total_score += 10
    else:
        details.append({"item": "正确剔除未参与花园活动的儿童 (Liam, Mason)", "score": 0, "max_score": 10, "passed": False, "reason": "逻辑漏洞: 错误包含了未去 Garden 的儿童"})

    # ---------------------------------------------------------
    # 7. 防止幻觉与捏造节点 (10分)
    # ---------------------------------------------------------
    valid_keys = {"Noah", "Chloe"}
    actual_keys = set(data.keys())
    # 一票否决额外主键
    if actual_keys.issubset(valid_keys) and len(actual_keys) <= 2:
        details.append({"item": "检查字典中是否有大模型捏造/多余的记录", "score": 10, "max_score": 10, "passed": True, "reason": "字典长度正常且未发现任何捏造的多余主键"})
        total_score += 10
    else:
        invalid_keys = actual_keys - valid_keys
        details.append({"item": "检查字典中是否有大模型捏造/多余的记录", "score": 0, "max_score": 10, "passed": False, "reason": f"严厉扣分: 发现幻觉或逻辑外的主键 {invalid_keys}"})

    # ---------------------------------------------------------
    # 8. 大模型语义探测: 纯净度检测 (10分)
    # ---------------------------------------------------------
    # 即使通过了精确包含，也要防止输出类似 "He had Celery Sticks after crying" 这样冗余的值
    llm_prompt = (
        "Check if ALL the values in this JSON mapping are strictly simple food/snack noun phrases "
        "(e.g., 'Celery Sticks', 'Carrot Sticks', 'Apples'). "
        "They MUST NOT contain full descriptive sentences, verbs, conversational fillers, or extra explanations "
        "like 'The safe snack is' or 'served after garden'. "
        "Answer 'YES' if they are perfectly clean and simple noun phrases, and 'NO' otherwise."
    )
    json_dump_str = json.dumps(data, indent=2)
    is_clean = llm_judge_content(llm_prompt, json_dump_str)
    if is_clean:
        details.append({"item": "利用大模型检查零食名称语义的纯净度", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定输出值符合纯名词短语的要求，无冗余对话"})
        total_score += 10
    else:
        details.append({"item": "利用大模型检查零食名称语义的纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定 JSON 值包含了啰嗦的句子或冗余描述"})

    # ---------------------------------------------------------
    # 最终结果输出
    # ---------------------------------------------------------
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
