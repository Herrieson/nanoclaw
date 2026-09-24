import os
import sys
import json
import re
import httpx
from openai import OpenAI

# =====================================================================
# 强制 API 规范: 初始化 OpenAI 客户端并关闭 SSL 验证
# =====================================================================
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
    """用于对非结构化文本的自然语言/格式要求进行大模型验证的统一接口"""
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
    # 接收沙盒工作区路径参数
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    # ---------------------------------------------------------
    # 1. 验证目标目录的建立 (10分)
    # ---------------------------------------------------------
    planning_dir = os.path.join(workspace, "planning")
    if os.path.isdir(planning_dir):
        total_score += 10
        score_details.append({"item": "检查 planning 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建 planning 目录"})
    else:
        score_details.append({"item": "检查 planning 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 planning 目录"})
    
    # ---------------------------------------------------------
    # 2. 验证重型设备志愿者名单 (50分)
    #    考察细粒度：提取准确率、黑名单规避、遵循指令的极简格式
    # ---------------------------------------------------------
    heavy_file = os.path.join(planning_dir, "heavy_equipment_volunteers.txt")
    if os.path.isfile(heavy_file):
        with open(heavy_file, "r", encoding="utf-8") as f:
            heavy_content = f.read()
            
        heavy_score = 0
        reasons = []
        
        # 精确结构化代码解析人名（忽略大小写和词缀影响）
        has_john = bool(re.search(r'\bjohn\b', heavy_content, re.IGNORECASE))
        has_dave = bool(re.search(r'\bdave\b', heavy_content, re.IGNORECASE))
        has_sarah = bool(re.search(r'\bsarah\b', heavy_content, re.IGNORECASE))
        has_bob = bool(re.search(r'\bbob\b', heavy_content, re.IGNORECASE))
        has_carl = bool(re.search(r'\bcarl\b', heavy_content, re.IGNORECASE))
        
        if has_john: 
            heavy_score += 10
            reasons.append("精准提取到 John (pickup truck)")
        if has_dave: 
            heavy_score += 10
            reasons.append("精准提取到 Dave (small backhoe)")
        if has_sarah: 
            heavy_score += 10
            reasons.append("精准提取到 Sarah (rented backhoe)")
            
        # 判定黑名单是否混入
        if has_bob or has_carl:
            # 严格惩罚机制
            reasons.append("严重错误：名单中未排除安全黑名单成员 Bob 或 Carl")
        else:
            reasons.append("成功避开安全黑名单成员")
            
            # 仅在无黑名单成员前提下，通过 LLM 验证非结构化文本的行文规范
            llm_prompt = (
                "Examine the following file content. Does it ONLY contain a simple list of names "
                "(like John, Dave, Sarah) WITHOUT any conversational filler, extra sentences, headers, "
                "or phrases like 'Here is the list'? A plain text list separated by commas or newlines is perfect. "
                "If it has any extra conversational text, answer NO."
            )
            is_clean_list = llm_judge_content(llm_prompt, heavy_content)
            
            if is_clean_list:
                heavy_score += 20
                reasons.append("严格遵循了 'Just their names is fine' 指令，格式极简")
            else:
                heavy_score += 10
                reasons.append("名单排除正确，但带有冗余对话修饰，未完全满足极简要求")
                
        total_score += heavy_score
        score_details.append({
            "item": "分析 heavy_equipment_volunteers.txt 内容与逻辑",
            "score": heavy_score,
            "max_score": 50,
            "passed": heavy_score == 50,
            "reason": "; ".join(reasons)
        })
    else:
        score_details.append({"item": "分析 heavy_equipment_volunteers.txt 内容与逻辑", "score": 0, "max_score": 50, "passed": False, "reason": "文件不存在"})
        
    # ---------------------------------------------------------
    # 3. 验证总工时统计计算 (40分)
    #    考察细粒度：数值准确性，拒绝模糊匹配
    # ---------------------------------------------------------
    hours_file = os.path.join(planning_dir, "total_hours.txt")
    if os.path.isfile(hours_file):
        with open(hours_file, "r", encoding="utf-8") as f:
            hours_content = f.read().strip()
            
        hours_score = 0
        hours_reason = ""
        
        # 仅使用确定性代码提取纯数字，严打结构化数据幻觉
        numbers = re.findall(r'\d+', hours_content)
        
        if len(numbers) == 1 and numbers[0] == "24":
            hours_score = 40
            hours_reason = "精确算出正确的有效总工时 24，且排除了黑名单时间，输出格式纯净"
        elif "24" in numbers:
            hours_score = 25
            hours_reason = "内容中包含正确的总工时 24，但违背了 'Just write that final, total valid hours number' 的纯数字要求，或掺杂了多余数字"
        elif "28" in numbers or "33" in numbers or "29" in numbers:
            hours_score = 0
            hours_reason = "严重计算错误：统计中未剔除安全黑名单人员的工时"
        else:
            hours_score = 0
            hours_reason = f"未找到正确数值 24，或产生了幻觉计算，提取到的数字列表为：{numbers}"
            
        total_score += hours_score
        score_details.append({
            "item": "分析 total_hours.txt 统计结果",
            "score": hours_score,
            "max_score": 40,
            "passed": hours_score == 40,
            "reason": hours_reason
        })
    else:
        score_details.append({"item": "分析 total_hours.txt 统计结果", "score": 0, "max_score": 40, "passed": False, "reason": "文件不存在"})

    # =====================================================================
    # 统一输出规范
    # =====================================================================
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
