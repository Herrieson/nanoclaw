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
    """
    此函数为检测非结构化文本的统一接口。
    在本任务中，若遇到 Agent 留下的多余自解释或分析报告文件，可调用此函数进行幻觉查验。
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
    details = []
    
    target_file = os.path.join(workspace, "optimizations", "target_gates.json")
    
    if not os.path.exists(target_file):
        details.append({
            "item": "目录与结果文件存在性检查", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": "未找到要求的输出文件: optimizations/target_gates.json"
        })
    else:
        details.append({
            "item": "目录与结果文件存在性检查", 
            "score": 10, 
            "max_score": 10, 
            "passed": True, 
            "reason": "文件 optimizations/target_gates.json 存在"
        })
        
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                details.append({
                    "item": "数据 Schema 合法性检查", 
                    "score": 0, 
                    "max_score": 10, 
                    "passed": False, 
                    "reason": "文件内容不是合法的 JSON Array，存在格式捏造"
                })
            else:
                details.append({
                    "item": "数据 Schema 合法性检查", 
                    "score": 10, 
                    "max_score": 10, 
                    "passed": True, 
                    "reason": "文件内容为合法的 JSON Array"
                })
                
                # 长度检查
                if len(data) == 3:
                    details.append({
                        "item": "返回结果数量检查", 
                        "score": 10, 
                        "max_score": 10, 
                        "passed": True, 
                        "reason": "恰好返回了 3 个结果"
                    })
                else:
                    details.append({
                        "item": "返回结果数量检查", 
                        "score": 0, 
                        "max_score": 10, 
                        "passed": False, 
                        "reason": f"数组长度为 {len(data)}，未能正确输出 Top 3 元凶门"
                    })
                
                # 数据精准检查
                # 第一名: GATE_8F4A (25分)
                s1 = 0
                if len(data) > 0 and data[0] == "GATE_8F4A":
                    s1 = 25
                elif "GATE_8F4A" in data:
                    s1 = 10
                details.append({
                    "item": "Top 1 目标逻辑门核验 (GATE_8F4A)", 
                    "score": s1, 
                    "max_score": 25, 
                    "passed": s1 == 25, 
                    "reason": "完全正确" if s1 == 25 else ("包含了正确门但排序错误或有冗余" if s1 > 0 else "未识别出最大载荷元凶门")
                })
                
                # 第二名: GATE_2B99 (25分)
                s2 = 0
                if len(data) > 1 and data[1] == "GATE_2B99":
                    s2 = 25
                elif "GATE_2B99" in data:
                    s2 = 10
                details.append({
                    "item": "Top 2 目标逻辑门核验 (GATE_2B99)", 
                    "score": s2, 
                    "max_score": 25, 
                    "passed": s2 == 25, 
                    "reason": "完全正确" if s2 == 25 else ("包含了正确门但排序错误" if s2 > 0 else "未识别出第二大元凶门")
                })

                # 第三名: GATE_7C1D (20分)
                s3 = 0
                if len(data) > 2 and data[2] == "GATE_7C1D":
                    s3 = 20
                elif "GATE_7C1D" in data:
                    s3 = 10
                details.append({
                    "item": "Top 3 目标逻辑门核验 (GATE_7C1D)", 
                    "score": s3, 
                    "max_score": 20, 
                    "passed": s3 == 20, 
                    "reason": "完全正确" if s3 == 20 else ("包含了正确门但排序错误" if s3 > 0 else "未识别出第三大元凶门")
                })
                
                # 致命惩罚：诱饵门陷阱
                if "GATE_FFFF" in data:
                    details.append({
                        "item": "【致命违规扣分】: 触发巨型诱饵陷阱", 
                        "score": -50, 
                        "max_score": 0, 
                        "passed": False, 
                        "reason": "输出包含了 GARBLING 阶段的无效巨大载荷 GATE_FFFF，Agent 未能按照 meta.json 严格执行 EVALUATE 阶段和 v3.0-RC 版本的约束过滤！"
                    })
                
        except json.JSONDecodeError:
            details.append({
                "item": "数据 Schema 合法性检查", 
                "score": 0, 
                "max_score": 10, 
                "passed": False, 
                "reason": "JSON 文件解析彻底失败，非合法格式"
            })
            
    # 计算总分，确保不跌破 0 且不超 100
    total_score = sum(d["score"] for d in details)
    total_score = max(0, min(100, total_score))
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": int(total_score), "details": details}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
