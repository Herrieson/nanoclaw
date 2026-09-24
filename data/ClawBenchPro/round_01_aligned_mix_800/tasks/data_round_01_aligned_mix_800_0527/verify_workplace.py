import os
import sys
import json
import httpx
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
    """用于验证自由文本中难以依靠正则保证精确归属的非结构化语义"""
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
    report_path = os.path.join(workspace, "boss_report.txt")
    
    details = []
    total_score = 0
    
    # 【检测项 1】报告生成与文件结构验证 (10分)
    if os.path.isfile(report_path):
        details.append({"item": "检查目标汇报文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "boss_report.txt 存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标汇报文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "boss_report.txt 未生成，全盘失败"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 读取最终文件内容
    with open(report_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    # 【检测项 2】代码严格匹配：提取目标车辆牌照 (15分)
    # 不允许使用模糊匹配去判断结构化核心字段，必须是字面完全一致
    target_plates = ["GHOST-88", "NEON-X", "RUST-01"]
    plates_score = 0
    missing_plates = []
    for p in target_plates:
        if p in content:
            plates_score += 5
        else:
            missing_plates.append(p)
            
    if plates_score == 15:
        details.append({"item": "精准提取有效故障车牌", "score": 15, "max_score": 15, "passed": True, "reason": "3个目标车牌均精准提取成功"})
    else:
        details.append({"item": "精准提取有效故障车牌", "score": plates_score, "max_score": 15, "passed": False, "reason": f"部分关键车牌遗漏: {missing_plates}"})
    total_score += plates_score

    # 【检测项 3】代码验证：字典序排序逻辑 (10分)
    if plates_score == 15:
        idx1, idx2, idx3 = content.find("GHOST-88"), content.find("NEON-X"), content.find("RUST-01")
        if idx1 < idx2 < idx3:
            details.append({"item": "车牌列表按字母顺序排序", "score": 10, "max_score": 10, "passed": True, "reason": "输出的车牌严格遵守了字母升序规范"})
            total_score += 10
        else:
            details.append({"item": "车牌列表按字母顺序排序", "score": 0, "max_score": 10, "passed": False, "reason": "提取了车牌但未能遵循字母表排序要求"})
    else:
        details.append({"item": "车牌列表按字母顺序排序", "score": 0, "max_score": 10, "passed": False, "reason": "前置条件未满足(车牌未完全提取)，无法判定排序分"})

    # 【检测项 4】代码验证：反幻觉与假阳性剔除 (10分)
    # "FAKE-1" 存在于 DRAFT 而非 FINAL 元数据中，检验 Agent 有没有误提取
    if "FAKE" in content or "FAKE-1" in content:
        details.append({"item": "剔除未打 FINAL 标签的无效车牌", "score": 0, "max_score": 10, "passed": False, "reason": "未能识别元数据标签，错误提取了诱饵车牌数据"})
    else:
        details.append({"item": "剔除未打 FINAL 标签的无效车牌", "score": 10, "max_score": 10, "passed": True, "reason": "成功排除了无效草稿状态(DRAFT)下的车牌"})
        total_score += 10
        
    # 【检测项 5】代码验证：火花塞库存结果的底层字面存在性 (10分)
    if "93" in content:
        details.append({"item": "物理验证库存结果是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到了正确的库存总和字面数值 '93'"})
        total_score += 10
    else:
        details.append({"item": "物理验证库存结果是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "结果报告中未找到计算正确的最终数值 '93'"})
        
    # 【检测项 6】LLM混合探针：库存结果的语义归属校验 (30分)
    # 防止 Agent 把 93 分配给别的变量(例如 93 个垫圈)，需强语义确认
    prompt_93 = "Carefully read the document. Does it explicitly and clearly state that the total count (or current stock) of 'Spark Plugs' is exactly 93? Do not hallucinate."
    if "93" in content and llm_judge_content(prompt_93, content):
        details.append({"item": "语义验证库存数值归属", "score": 30, "max_score": 30, "passed": True, "reason": "大模型探针确认数值 93 在语境中准确对应火花塞总库存"})
        total_score += 30
    else:
        details.append({"item": "语义验证库存数值归属", "score": 0, "max_score": 30, "passed": False, "reason": "未能通过大模型语义防伪检测(归属错误或缺失)"})

    # 【检测项 7】LLM混合探针：角色扮演与商业报告格式 (15分)
    prompt_tone = "Is this document formatted as a professional 'End-of-Month Critical Liability Report' addressed to a boss, exhibiting a formal/professional tone rather than casual chat or raw code outputs?"
    if llm_judge_content(prompt_tone, content):
        details.append({"item": "专业语气与汇报版式验证", "score": 15, "max_score": 15, "passed": True, "reason": "符合 Persona 要求的危机汇报格式与老板汇报口吻"})
        total_score += 15
    else:
        details.append({"item": "专业语气与汇报版式验证", "score": 0, "max_score": 15, "passed": False, "reason": "报告缺乏对应的老板汇报属性或排版过于粗糙草率"})

    # 输出持久化评分文件
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
