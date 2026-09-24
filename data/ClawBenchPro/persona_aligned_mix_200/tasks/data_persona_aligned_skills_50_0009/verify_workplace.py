import os
import sys
import json
import httpx
from openai import OpenAI

# 强制要求的 API 规范核心逻辑（虽本任务以强代码校验为主，但保留以作规范支持）
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
    target_file = os.path.join(workspace, "output", "critical_state.json")
    
    score_details = []
    total_score = 0

    def add_score(item, score, max_score, passed, reason):
        nonlocal total_score
        total_score += score
        score_details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    if not os.path.exists(target_file):
        add_score("产物 JSON 文件存在且可被解析", 0, 15, False, "文件 output/critical_state.json 未生成或不存在")
        add_score("输出字段名称合法且无捏造多余字段", 0, 15, False, "前置依赖失败")
        add_score("latest_quaternion 数据类型正确", 0, 10, False, "前置依赖失败")
        add_score("latest_quaternion 数值准确", 0, 25, False, "前置依赖失败")
        add_score("max_temperature 数据类型正确", 0, 10, False, "前置依赖失败")
        add_score("max_temperature 数值准确", 0, 25, False, "前置依赖失败")
    else:
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            add_score("产物 JSON 文件存在且可被解析", 15, 15, True, "成功解析目标 JSON 文件")
            
            # 严格检查 Keys
            keys = set(data.keys())
            expected_keys = {"latest_quaternion", "max_temperature"}
            if keys == expected_keys:
                add_score("输出字段名称合法且无捏造多余字段", 15, 15, True, "严格匹配规定的两个字段，无多余内容")
            elif expected_keys.issubset(keys):
                add_score("输出字段名称合法且无捏造多余字段", 5, 15, False, f"包含必须字段，但涉嫌幻觉捏造多余字段: {keys - expected_keys}")
            else:
                add_score("输出字段名称合法且无捏造多余字段", 0, 15, False, f"缺失必须的业务字段: {expected_keys - keys}")
            
            # 检查 latest_quaternion
            q = data.get("latest_quaternion")
            if isinstance(q, list) and len(q) == 4 and all(isinstance(x, (int, float)) for x in q):
                add_score("latest_quaternion 数据类型正确", 10, 10, True, "类型为长度为 4 的数字数组")
                
                # 校验提取最新的星象仪数据: [0.4999, 0.5001, -0.4999, -0.5001]
                expected_q = [0.4999, 0.5001, -0.4999, -0.5001]
                match = True
                for a, b in zip(q, expected_q):
                    if abs(a - b) > 0.00015:  # 考虑浮点误差与题目要求4位小数
                        match = False
                if match:
                    add_score("latest_quaternion 数值准确", 25, 25, True, f"四元数解析成功，正确提取出最新一帧的时间戳并解码大端浮点数: {q}")
                else:
                    add_score("latest_quaternion 数值准确", 0, 25, False, f"数值不匹配(可能是未提取最新帧，或大小端解码错误): {q}")
            else:
                add_score("latest_quaternion 数据类型正确", 0, 10, False, f"类型非数字数组或长度不为 4: {type(q)}")
                add_score("latest_quaternion 数值准确", 0, 25, False, "类型错误，无法对比数值")

            # 检查 max_temperature
            t = data.get("max_temperature")
            if isinstance(t, (int, float)):
                add_score("max_temperature 数据类型正确", 10, 10, True, "类型为数字")
                
                # 校验提取最高温度 ADC(2695) 且通过 Tool 转换后的摄氏度 (94.75)
                if abs(t - 94.75) < 0.015:
                    add_score("max_temperature 数值准确", 25, 25, True, f"成功找出温度峰值，并使用了工具将其转换为摄氏度: {t}")
                else:
                    add_score("max_temperature 数值准确", 0, 25, False, f"数值不匹配(可能是未找全最高峰值、使用了错误 ADC 值、未调用 Toolkit 或编造): {t}")
            else:
                add_score("max_temperature 数据类型正确", 0, 10, False, f"类型非数字: {type(t)}")
                add_score("max_temperature 数值准确", 0, 25, False, "类型错误，无法对比数值")

        except json.JSONDecodeError:
            add_score("产物 JSON 文件存在且可被解析", 0, 15, False, "文件存在但格式并非合法 JSON")
            add_score("输出字段名称合法且无捏造多余字段", 0, 15, False, "解析失败无法检查")
            add_score("latest_quaternion 数据类型正确", 0, 10, False, "解析失败无法检查")
            add_score("latest_quaternion 数值准确", 0, 25, False, "解析失败无法检查")
            add_score("max_temperature 数据类型正确", 0, 10, False, "解析失败无法检查")
            add_score("max_temperature 数值准确", 0, 25, False, "解析失败无法检查")

    # 结果输出
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
