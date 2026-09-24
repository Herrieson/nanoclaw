import os
import sys
import json
import httpx
import glob
from openai import OpenAI

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
    """大模型统一检测非结构化文本接口"""
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
    score_details = []
    total_score = 0
    
    # 验证项 1: 检查目标目录是否存在 (原生代码) - 10分
    target_dir = os.path.join(workspace, "prep_work")
    dir_exists = os.path.isdir(target_dir)
    if dir_exists:
        score_details.append({"item": "检查结果目录 prep_work 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建了 prep_work 目录"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录 prep_work 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 prep_work 目录"})
        
    # 验证项 2: 检查结果文件是否存在 (原生代码) - 10分
    file_content = ""
    if dir_exists:
        files = glob.glob(os.path.join(target_dir, "*"))
        files = [f for f in files if os.path.isfile(f)]
        if len(files) > 0:
            score_details.append({"item": "检查 prep_work 目录下是否生成了文件", "score": 10, "max_score": 10, "passed": True, "reason": f"找到了输出文件: {os.path.basename(files[0])}"})
            total_score += 10
            try:
                with open(files[0], 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except Exception as e:
                pass
        else:
            score_details.append({"item": "检查 prep_work 目录下是否生成了文件", "score": 0, "max_score": 10, "passed": False, "reason": "prep_work 目录为空"})
    else:
        score_details.append({"item": "检查 prep_work 目录下是否生成了文件", "score": 0, "max_score": 10, "passed": False, "reason": "由于目录不存在，无法寻找文件"})

    # 验证项 3: 检查鸡尾酒推荐的准确性 (LLM 语义分析) - 40分
    # 正确结果应该是唯一推荐 "Missouri Mule"。因为 Irish Sunrise 缺摔碎的 Grenadine，Midwest Fidget 缺发霉的 Simple Syrup 和缺货的 Bourbon。
    if file_content.strip():
        cocktail_prompt = (
            "Evaluate if the provided document clearly and exclusively recommends ONLY 'Missouri Mule' as the winning or available cocktail to pitch. "
            "If it recommends 'Irish Sunrise' or 'Midwest Fidget' as viable options, or fails to mention 'Missouri Mule', answer NO. "
            "If it explains that the other two cannot be made due to missing/spoiled ingredients and correctly identifies 'Missouri Mule' as the only feasible option, answer YES."
        )
        passed_cocktail = llm_judge_content(cocktail_prompt, file_content)
        if passed_cocktail:
            score_details.append({"item": "鸡尾酒交叉筛选准确性判断", "score": 40, "max_score": 40, "passed": True, "reason": "成功排除了损坏和缺货的原料，准确唯一推荐了 Missouri Mule"})
            total_score += 40
        else:
            score_details.append({"item": "鸡尾酒交叉筛选准确性判断", "score": 0, "max_score": 40, "passed": False, "reason": "未能准确筛选出唯一可用的鸡尾酒 Missouri Mule (可能是未听取录音或未比对库存)"})
            
        # 验证项 4: 检查净小费金额的准确性 (LLM 语义分析) - 40分
        # 正确结果：总毛利 350.00，税后净利 308.00
        tip_prompt = (
            "Evaluate if the provided document states Danny's final net take-home tip total (after the 12% Clean Air Tax) is exactly $308.00 (or 308). "
            "Look closely for the final net amount. If the document claims the final net amount is anything other than 308 (e.g., 350, 200, 308.12), answer NO. "
            "If it clearly states 308 or 308.00 as the final net tip amount, answer YES."
        )
        passed_tip = llm_judge_content(tip_prompt, file_content)
        if passed_tip:
            score_details.append({"item": "净小费金额计算准确性判断", "score": 40, "max_score": 40, "passed": True, "reason": "准确解析了异构CSV中的提成比例，并成功计算出税后净小费 308.00"})
            total_score += 40
        else:
            score_details.append({"item": "净小费金额计算准确性判断", "score": 0, "max_score": 40, "passed": False, "reason": "未能在文档中找到正确的最终税后净小费金额 308.00"})
    else:
        score_details.append({"item": "鸡尾酒交叉筛选准确性判断", "score": 0, "max_score": 40, "passed": False, "reason": "文件内容为空，无法验证"})
        score_details.append({"item": "净小费金额计算准确性判断", "score": 0, "max_score": 40, "passed": False, "reason": "文件内容为空，无法验证"})

    # 输出结果文件
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(f"Validation completed. Score: {total_score}/100")

if __name__ == "__main__":
    verify()
