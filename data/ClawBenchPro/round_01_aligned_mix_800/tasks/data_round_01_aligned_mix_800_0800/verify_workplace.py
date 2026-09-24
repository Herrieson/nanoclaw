#!/usr/bin/env python3
import os
import sys
import json
import httpx
import re
from openai import OpenAI

# ---------------------------------------------------------
# API 配置：强制使用环境变量并关闭 SSL 验证
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
    """
    使用大模型进行非结构化文本的语义验证（例如语气、专业性检测）。
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    briefing_dir = os.path.join(workspace, "briefing")
    
    score = 0
    details = []

    # =====================================================================
    # 1. 结构与文件生成检查 (满分 10 分)
    # =====================================================================
    content = ""
    if not os.path.isdir(briefing_dir):
        details.append({"item": "检查 briefing 目录", "score": 0, "max_score": 10, "passed": False, "reason": "briefing 目录被误删或不存在"})
    else:
        files = [f for f in os.listdir(briefing_dir) if os.path.isfile(os.path.join(briefing_dir, f))]
        if not files:
            details.append({"item": "检查报告文件生成", "score": 0, "max_score": 10, "passed": False, "reason": "briefing 目录中未找到任何输出文件"})
        else:
            details.append({"item": "检查报告文件生成", "score": 10, "max_score": 10, "passed": True, "reason": f"成功生成报告文件: {', '.join(files)}"})
            score += 10
            
            # 读取所有生成的文件内容进行后续综合验证
            content_list = []
            for bf in files:
                try:
                    with open(os.path.join(briefing_dir, bf), "r", encoding="utf-8") as f:
                        content_list.append(f.read())
                except Exception:
                    pass
            content = "\n".join(content_list)
            
    # 若无内容，后续验证均判为 0 分
    if not content.strip():
        details.append({"item": "精准提取未注册车牌", "score": 0, "max_score": 40, "passed": False, "reason": "文件无内容"})
        details.append({"item": "严格过滤错误车牌 (无假阳性)", "score": 0, "max_score": 30, "passed": False, "reason": "文件无内容"})
        details.append({"item": "LLM 语义验证：报告专业性", "score": 0, "max_score": 20, "passed": False, "reason": "文件无内容"})
    else:
        # =====================================================================
        # 2 & 3. 确定性核心数据校验 (满分 70 分，强制代码层解析，严禁模糊匹配)
        # =====================================================================
        content_upper = content.upper()
        # 精准匹配加州车牌格式进行提取
        extracted_plates = set(re.findall(r'CA-[A-Z0-9]+', content_upper))
        expected_plates = {"CA-9FAKE00", "CA-BAD888"}
        
        # [2] 检查是否精准找出未注册车牌 (40 分)
        missing = expected_plates - extracted_plates
        if not missing:
            details.append({"item": "精准提取未注册车牌", "score": 40, "max_score": 40, "passed": True, "reason": "成功找出所有未注册车牌 (CA-9FAKE00, CA-BAD888)"})
            score += 40
        elif len(missing) == 1:
            details.append({"item": "精准提取未注册车牌", "score": 20, "max_score": 40, "passed": False, "reason": f"部分找出未注册车牌，遗漏: {missing}"})
            score += 20
        else:
            details.append({"item": "精准提取未注册车牌", "score": 0, "max_score": 40, "passed": False, "reason": "完全未能找出正确的未注册车牌"})
            
        # [3] 检查是否混入已注册车牌或出现幻觉车牌 (30 分)
        false_positives = extracted_plates - expected_plates
        if not false_positives:
            details.append({"item": "严格过滤错误车牌 (无假阳性)", "score": 30, "max_score": 30, "passed": True, "reason": "未在报告中混入已合法注册或捏造的车牌"})
            score += 30
        else:
            details.append({"item": "严格过滤错误车牌 (无假阳性)", "score": 0, "max_score": 30, "passed": False, "reason": f"严重错误！报告中混入了错误车牌: {false_positives}"})
            
        # =====================================================================
        # 4. LLM 语义检测：非结构化要求 (满分 20 分)
        # =====================================================================
        prompt = (
            "Evaluate if the following report meets these strict professional criteria:\n"
            "1. It is a clean, formal summary appropriate for a police captain.\n"
            "2. It ONLY reports on the unauthorized/unregistered plates.\n"
            "3. It does NOT contain casual complaints, officer's personal issues (like a soccer game), or frustrations about IT.\n"
            "Does the report perfectly meet these criteria?"
        )
        llm_result = llm_judge_content(prompt, content)
        if llm_result:
            details.append({"item": "LLM 语义验证：报告专业性", "score": 20, "max_score": 20, "passed": True, "reason": "LLM 判定报告语气专业，且已滤除原作者的私人情绪和冗余吐槽。"})
            score += 20
        else:
            details.append({"item": "LLM 语义验证：报告专业性", "score": 0, "max_score": 20, "passed": False, "reason": "LLM 判定报告仍包含非专业的个人情绪（如足球比赛、IT 吐槽）或格式混乱。"})
            
    # 统一输出评分结果
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
