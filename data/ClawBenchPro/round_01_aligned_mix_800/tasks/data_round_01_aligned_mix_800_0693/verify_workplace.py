import os
import sys
import json
import re
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证 (供非结构化文本验证备用)
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """用于自然语言检测的辅助方法。本任务高度结构化，优先使用确定性原生代码解析"""
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
    
    total_score = 0
    details = []
    
    prep_dir = os.path.join(workspace, "delivery_prep")
    problem_file = os.path.join(prep_dir, "problem_packages.txt")
    summary_file = os.path.join(prep_dir, "route_summary.json")
    
    # 1. 验证目标目录 (10分)
    if os.path.isdir(prep_dir):
        total_score += 10
        details.append({"item": "验证 delivery_prep 目录的存在性", "score": 10, "max_score": 10, "passed": True, "reason": "目录已成功创建。"})
    else:
        details.append({"item": "验证 delivery_prep 目录的存在性", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 delivery_prep 目录。"})
    
    # 2. 验证 problem_packages.txt 及内容 (10分存在性 + 30分内容)
    if os.path.isfile(problem_file):
        total_score += 10
        details.append({"item": "验证 problem_packages.txt 文件的存在性", "score": 10, "max_score": 10, "passed": True, "reason": "文件已创建。"})
        
        # 严格检查筛选结果：
        # PKG-1002 (>50 lbs)
        # PKG-1003 (Zip 4 chars)
        # PKG-2002 (>50 lbs)
        # PKG-2004 (Zip non-digit)
        # PKG-3002 (>50 lbs)
        # 注意 PKG-3003 (50.0 lbs) 不应被包含
        expected_problems = {"PKG-1002", "PKG-1003", "PKG-2002", "PKG-2004", "PKG-3002"}
        try:
            with open(problem_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 使用正则抓取包号以应对 Agent 可能增加的额外描述，但严格校验集合
            found_packages = set(re.findall(r'PKG-\d{4}', content))
            
            if found_packages == expected_problems:
                score = 30
                details.append({"item": "验证问题包裹名单内容的准确性", "score": score, "max_score": 30, "passed": True, "reason": "准确地筛选出了所有超重及无效Zip的包裹，无遗漏无幻觉。"})
            else:
                missing = expected_problems - found_packages
                extra = found_packages - expected_problems
                
                # 扣分逻辑：缺失一个扣 10 分，多余一个扣 10 分
                deduction = len(missing) * 10 + len(extra) * 10
                score = max(0, 30 - deduction)
                details.append({
                    "item": "验证问题包裹名单内容的准确性", 
                    "score": score, 
                    "max_score": 30, 
                    "passed": score == 30, 
                    "reason": f"集合不匹配。缺失: {missing if missing else '无'}, 多余/错误包含: {extra if extra else '无'}"
                })
            total_score += score
        except Exception as e:
            details.append({"item": "验证问题包裹名单内容的准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"文件读取出错: {e}"})
    else:
        details.append({"item": "验证 problem_packages.txt 文件的存在性", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 problem_packages.txt。"})
        details.append({"item": "验证问题包裹名单内容的准确性", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在，跳过内容检查。"})

    # 3. 验证 route_summary.json 及其内容 (10分存在性 + 40分内容)
    if os.path.isfile(summary_file):
        total_score += 10
        details.append({"item": "验证 route_summary.json 文件的存在性", "score": 10, "max_score": 10, "passed": True, "reason": "文件已创建。"})
        
        # 严格检查 JSON Schema 和正确的统计
        expected_summary = {
            "90210": 3,
            "90001": 2,
            "33101": 1
        }
        
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                summary_data = json.load(f)
            
            # 防御性转换：确保比较时都是字符串键和整型值
            formatted_data = {str(k): int(v) for k, v in summary_data.items() if str(k).strip()}
            formatted_expected = {str(k): v for k, v in expected_summary.items()}
            
            if formatted_data == formatted_expected:
                score = 40
                details.append({"item": "验证路线汇总统计JSON的准确性", "score": score, "max_score": 40, "passed": True, "reason": "有效的Zip Code及其合法包裹数目的统计完美吻合。"})
            else:
                score = 0
                match_count = sum(1 for k, v in formatted_expected.items() if formatted_data.get(k) == v)
                extra_keys = set(formatted_data.keys()) - set(formatted_expected.keys())
                
                # 算分：每个正确的合法项+15分，每个捏造的多余项-10分。最多不超过40分。
                score = max(0, match_count * 15 - len(extra_keys) * 10)
                score = min(score, 40)
                
                details.append({
                    "item": "验证路线汇总统计JSON的准确性", 
                    "score": score, 
                    "max_score": 40, 
                    "passed": False, 
                    "reason": f"数据存在错误或幻觉。预期：{formatted_expected}，实际检测到：{formatted_data}"
                })
            total_score += score
            
        except json.JSONDecodeError:
            details.append({"item": "验证路线汇总统计JSON的准确性", "score": 0, "max_score": 40, "passed": False, "reason": "严重错误：输出的文件不是合法的 JSON 格式。"})
        except Exception as e:
            details.append({"item": "验证路线汇总统计JSON的准确性", "score": 0, "max_score": 40, "passed": False, "reason": f"解析或类型转换出错: {e}"})
    else:
        details.append({"item": "验证 route_summary.json 文件的存在性", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 route_summary.json。"})
        details.append({"item": "验证路线汇总统计JSON的准确性", "score": 0, "max_score": 40, "passed": False, "reason": "文件不存在，跳过内容检查。"})

    # 4. 汇总写出结果
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
